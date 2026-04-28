from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_user
from models.category import Category
from models.decision import Decision
from models.project import Project
from models.room import Room
from models.user import User
from schemas.decision import DecisionCreate, DecisionResponse

router = APIRouter()


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


async def _user_decision(db: AsyncSession, decision_id: str, user_id: str) -> Decision:
    try:
        did = UUID(decision_id)
        uid = UUID(user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found"
        ) from exc

    result = await db.execute(
        select(Decision)
        .join(Category, Category.id == Decision.category_id)
        .join(Room, Room.id == Category.room_id)
        .join(Project, Project.id == Room.project_id)
        .where(Decision.id == did, Project.user_id == uid)
    )
    decision = result.scalar_one_or_none()
    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found"
        )
    return decision


@router.get(
    "/categories/{category_id}/decisions", response_model=list[DecisionResponse]
)
async def list_decisions(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DecisionResponse]:
    category = await _user_category(db, category_id, str(current_user.id))
    result = await db.execute(
        select(Decision)
        .where(Decision.category_id == category.id)
        .order_by(Decision.created_at.asc())
    )
    decisions = result.scalars().all()
    return [
        DecisionResponse.model_validate(
            {
                **decision.__dict__,
                "id": str(decision.id),
                "category_id": str(decision.category_id),
                "product_id": str(decision.product_id) if decision.product_id else None,
            }
        )
        for decision in decisions
    ]


@router.post(
    "/categories/{category_id}/decisions",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_decision(
    category_id: str,
    payload: DecisionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DecisionResponse:
    category = await _user_category(db, category_id, str(current_user.id))
    product_id = UUID(payload.product_id) if payload.product_id else None

    decision = Decision(
        category_id=category.id,
        product_id=product_id,
        decision_type=payload.decision_type,
        rationale=payload.rationale,
        source=payload.source,
    )
    db.add(decision)
    await db.flush()
    return DecisionResponse.model_validate(
        {
            **decision.__dict__,
            "id": str(decision.id),
            "category_id": str(decision.category_id),
            "product_id": str(decision.product_id) if decision.product_id else None,
        }
    )


@router.delete("/decisions/{decision_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_decision(
    decision_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    decision = await _user_decision(db, decision_id, str(current_user.id))
    await db.delete(decision)
