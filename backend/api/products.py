from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db
from core.dependencies import get_current_user
from models.category import Category
from models.product import Product
from models.project import Project
from models.room import Room
from models.user import User
from schemas.product import ProductCreate, ProductResponse, ProductUpdate
from services.ai_service import summarize_product_specs

router = APIRouter()
_CATEGORIES_DIR = Path(__file__).resolve().parents[2] / "categories"


class ScrapeRequest(BaseModel):
    url: HttpUrl


def _category_schema(slug: str) -> dict:
    schema_path = _CATEGORIES_DIR / f"{slug}.json"
    if not schema_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category schema not found"
        )
    return json.loads(schema_path.read_text(encoding="utf-8"))


async def _user_category(db: AsyncSession, category_id: str, user_id: str) -> Category:
    try:
        cid = UUID(category_id)
        uid = UUID(user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        ) from exc

    result = await db.execute(
        select(Category)
        .join(Room, Room.id == Category.room_id)
        .join(Project, Project.id == Room.project_id)
        .where(Category.id == cid, Project.user_id == uid)
    )
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return category


async def _user_product(db: AsyncSession, product_id: str, user_id: str) -> Product:
    try:
        pid = UUID(product_id)
        uid = UUID(user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        ) from exc

    result = await db.execute(
        select(Product)
        .join(Category, Category.id == Product.category_id)
        .join(Room, Room.id == Category.room_id)
        .join(Project, Project.id == Room.project_id)
        .where(Product.id == pid, Project.user_id == uid)
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return product


@router.get("/categories/{category_id}/products", response_model=list[ProductResponse])
async def list_products(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProductResponse]:
    category = await _user_category(db, category_id, str(current_user.id))
    result = await db.execute(
        select(Product)
        .where(Product.category_id == category.id)
        .order_by(Product.created_at.desc())
    )
    products = result.scalars().all()
    return [
        ProductResponse.model_validate(
            {
                **product.__dict__,
                "id": str(product.id),
                "category_id": str(product.category_id),
            }
        )
        for product in products
    ]


@router.post(
    "/categories/{category_id}/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    category_id: str,
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductResponse:
    category = await _user_category(db, category_id, str(current_user.id))
    product = Product(category_id=category.id, **payload.model_dump())
    db.add(product)
    await db.flush()
    return ProductResponse.model_validate(
        {
            **product.__dict__,
            "id": str(product.id),
            "category_id": str(product.category_id),
        }
    )


@router.post(
    "/categories/{category_id}/products/scrape",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def scrape_product(
    category_id: str,
    payload: ScrapeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductResponse:
    category = await _user_category(db, category_id, str(current_user.id))

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            scrape_response = await client.post(
                f"{settings.scraper_service_url}/scrape",
                json={"url": str(payload.url), "category_slug": category.category_slug},
            )
            scrape_response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Scraper service error"
        ) from exc

    scraped = scrape_response.json()
    product = Product(
        category_id=category.id,
        source_url=str(payload.url),
        retailer=scraped.get("retailer"),
        name=scraped.get("name") or str(payload.url),
        price=scraped.get("price"),
        currency=scraped.get("currency") or "USD",
        images=scraped.get("images") or [],
        category_slug=category.category_slug,
        attributes=scraped.get("attributes") or {},
        raw_specs=scraped.get("raw_specs") or scraped,
        scraped_at=datetime.now(timezone.utc),
        status="researching",
        is_manual=False,
    )
    db.add(product)
    await db.flush()

    return ProductResponse.model_validate(
        {
            **product.__dict__,
            "id": str(product.id),
            "category_id": str(product.category_id),
        }
    )


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductResponse:
    product = await _user_product(db, product_id, str(current_user.id))
    return ProductResponse.model_validate(
        {
            **product.__dict__,
            "id": str(product.id),
            "category_id": str(product.category_id),
        }
    )


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    payload: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductResponse:
    product = await _user_product(db, product_id, str(current_user.id))
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    await db.flush()
    return ProductResponse.model_validate(
        {
            **product.__dict__,
            "id": str(product.id),
            "category_id": str(product.category_id),
        }
    )


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    product = await _user_product(db, product_id, str(current_user.id))
    await db.delete(product)


@router.post("/products/{product_id}/summarize")
async def summarize_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    product = await _user_product(db, product_id, str(current_user.id))
    category = await _user_category(db, str(product.category_id), str(current_user.id))

    schema = _category_schema(category.category_slug)
    summary = await summarize_product_specs(
        {
            "id": str(product.id),
            "name": product.name,
            "price": product.price,
            "currency": product.currency,
            "attributes": product.attributes,
            "raw_specs": product.raw_specs,
        },
        schema,
    )
    return {"product_id": str(product.id), "summary": summary}
