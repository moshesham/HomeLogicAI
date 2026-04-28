from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.config import settings
from core.database import get_db
from core.dependencies import get_current_user
from models.category import Category
from models.product import Product
from models.project import Project
from models.room import Room
from models.user import User
from schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from services.ai_service import generate_comparison_summary

router = APIRouter()
_CATEGORIES_DIR = Path(__file__).resolve().parents[2] / "categories"


def _category_schema(slug: str) -> dict:
    schema_path = _CATEGORIES_DIR / f"{slug}.json"
    if not schema_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category schema not found")
    return json.loads(schema_path.read_text(encoding="utf-8"))


async def _user_category(db: AsyncSession, category_id: str, user_id: str) -> Category:
    try:
        cid = UUID(category_id)
        uid = UUID(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found") from exc

    result = await db.execute(
        select(Category)
        .join(Room, Room.id == Category.room_id)
        .join(Project, Project.id == Room.project_id)
        .where(Category.id == cid, Project.user_id == uid)
        .options(selectinload(Category.products), selectinload(Category.decisions))
    )
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.get("/rooms/{room_id}/categories", response_model=list[CategoryResponse])
async def list_categories(
    room_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CategoryResponse]:
    try:
        rid = UUID(room_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found") from exc

    room_result = await db.execute(
        select(Room)
        .join(Project, Project.id == Room.project_id)
        .where(Room.id == rid, Project.user_id == current_user.id)
    )
    if room_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    result = await db.execute(
        select(Category)
        .where(Category.room_id == rid)
        .options(selectinload(Category.products), selectinload(Category.decisions))
        .order_by(Category.display_order, Category.created_at)
    )
    categories = result.scalars().all()
    return [
        CategoryResponse.model_validate(
            {
                **category.__dict__,
                "id": str(category.id),
                "room_id": str(category.room_id),
                "selected_product_id": str(category.selected_product_id) if category.selected_product_id else None,
            }
        )
        for category in categories
    ]


@router.post("/rooms/{room_id}/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    room_id: str,
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryResponse:
    try:
        rid = UUID(room_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found") from exc

    room_result = await db.execute(
        select(Room)
        .join(Project, Project.id == Room.project_id)
        .where(Room.id == rid, Project.user_id == current_user.id)
    )
    if room_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    _category_schema(payload.category_slug)

    category = Category(room_id=rid, **payload.model_dump())
    db.add(category)
    await db.flush()
    return CategoryResponse.model_validate(
        {
            **category.__dict__,
            "id": str(category.id),
            "room_id": str(category.room_id),
            "selected_product_id": str(category.selected_product_id) if category.selected_product_id else None,
        }
    )


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryResponse:
    category = await _user_category(db, category_id, str(current_user.id))
    return CategoryResponse.model_validate(
        {
            **category.__dict__,
            "id": str(category.id),
            "room_id": str(category.room_id),
            "selected_product_id": str(category.selected_product_id) if category.selected_product_id else None,
        }
    )


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryResponse:
    category = await _user_category(db, category_id, str(current_user.id))

    updates = payload.model_dump(exclude_unset=True)
    if "category_slug" in updates:
        _category_schema(updates["category_slug"])

    for field, value in updates.items():
        setattr(category, field, value)
    await db.flush()

    return CategoryResponse.model_validate(
        {
            **category.__dict__,
            "id": str(category.id),
            "room_id": str(category.room_id),
            "selected_product_id": str(category.selected_product_id) if category.selected_product_id else None,
        }
    )


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    category = await _user_category(db, category_id, str(current_user.id))
    await db.delete(category)


@router.get("/categories/{category_id}/compare")
async def compare_category_products(
    category_id: str,
    product_ids: list[str] | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    category = await _user_category(db, category_id, str(current_user.id))

    query = select(Product).where(Product.category_id == category.id).order_by(Product.created_at.desc())
    if product_ids:
        ids = []
        for product_id in product_ids:
            try:
                ids.append(UUID(product_id))
            except ValueError as exc:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid product id") from exc
        query = query.where(Product.id.in_(ids))
    else:
        query = query.limit(settings.max_compare_products)

    result = await db.execute(query)
    products = result.scalars().all()

    if not 2 <= len(products) <= settings.max_compare_products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Comparison requires 2-{settings.max_compare_products} products",
        )

    category_schema = _category_schema(category.category_slug)
    products_payload = [
        {
            "id": str(product.id),
            "name": product.name,
            "price": product.price,
            "currency": product.currency,
            "attributes": product.attributes,
            "status": product.status,
        }
        for product in products
    ]
    summary = await generate_comparison_summary(products_payload, category_schema)

    return {
        "category_id": str(category.id),
        "category_slug": category.category_slug,
        "products": products_payload,
        "summary": summary,
    }


@router.get("/guides/{category_slug}")
async def get_buyer_guide(category_slug: str) -> dict:
    return _category_schema(category_slug)
