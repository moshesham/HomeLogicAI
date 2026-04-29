from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import get_db
from core.dependencies import get_current_user
from models.category import Category
from models.project import Project
from models.room import Room
from models.user import User
from schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from services.storage_service import delete_project_folder, get_project_path

router = APIRouter()


def _project_budget_summary(project: Project) -> dict[str, float | None]:
    allocated = 0.0
    actual = 0.0
    has_allocated = False
    has_actual = False
    for room in project.rooms:
        for category in room.categories:
            if category.budget_allocated is not None:
                allocated += float(category.budget_allocated)
                has_allocated = True
            if category.budget_actual is not None:
                actual += float(category.budget_actual)
                has_actual = True
    return {
        "total_budget": project.total_budget,
        "allocated": allocated if has_allocated else None,
        "actual": actual if has_actual else None,
        "remaining": (
            (project.total_budget - actual)
            if project.total_budget is not None and has_actual
            else None
        ),
    }


async def _get_user_project(db: AsyncSession, project_id: str, user_id: str) -> Project:
    try:
        pid = UUID(project_id)
        uid = UUID(user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        ) from exc

    result = await db.execute(
        select(Project)
        .where(Project.id == pid, Project.user_id == uid)
        .options(selectinload(Project.rooms).selectinload(Room.categories))
    )
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return project


@router.get("/projects", response_model=list[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProjectResponse]:
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .options(selectinload(Project.rooms).selectinload(Room.categories))
        .order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()

    return [
        ProjectResponse.model_validate(
            {
                **project.__dict__,
                "id": str(project.id),
                "user_id": str(project.user_id),
                "room_count": len(project.rooms),
                "budget_summary": _project_budget_summary(project),
            }
        )
        for project in projects
    ]


@router.post(
    "/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED
)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    project = Project(user_id=current_user.id, **payload.model_dump())
    db.add(project)
    await db.flush()
    get_project_path(str(project.id)).mkdir(parents=True, exist_ok=True)

    return ProjectResponse.model_validate(
        {
            **project.__dict__,
            "id": str(project.id),
            "user_id": str(project.user_id),
            "room_count": 0,
            # New projects have no rooms yet — avoid lazy-loading the relationship.
            "budget_summary": {
                "total_budget": project.total_budget,
                "allocated": None,
                "actual": None,
                "remaining": None,
            },
            "rooms": [],
        }
    )


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    project = await _get_user_project(db, project_id, str(current_user.id))
    return ProjectResponse.model_validate(
        {
            **project.__dict__,
            "id": str(project.id),
            "user_id": str(project.user_id),
            "room_count": len(project.rooms),
            "budget_summary": _project_budget_summary(project),
        }
    )


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    project = await _get_user_project(db, project_id, str(current_user.id))
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    await db.flush()

    return ProjectResponse.model_validate(
        {
            **project.__dict__,
            "id": str(project.id),
            "user_id": str(project.user_id),
            "room_count": len(project.rooms),
            "budget_summary": _project_budget_summary(project),
        }
    )


@router.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    project = await _get_user_project(db, project_id, str(current_user.id))
    await db.delete(project)
    delete_project_folder(str(project.id))


@router.get("/projects/{project_id}/budget")
async def project_budget_breakdown(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    project = await _get_user_project(db, project_id, str(current_user.id))

    rooms_payload = []
    for room in project.rooms:
        room_categories = await db.execute(
            select(Category)
            .where(Category.room_id == room.id)
            .order_by(Category.display_order)
        )
        categories = room_categories.scalars().all()
        rooms_payload.append(
            {
                "room_id": str(room.id),
                "room_name": room.name,
                "room_budget": room.room_budget,
                "categories": [
                    {
                        "category_id": str(cat.id),
                        "category_slug": cat.category_slug,
                        "display_name": cat.display_name,
                        "budget_allocated": cat.budget_allocated,
                        "budget_actual": cat.budget_actual,
                        "budget_estimated_low": cat.budget_estimated_low,
                        "budget_estimated_high": cat.budget_estimated_high,
                    }
                    for cat in categories
                ],
            }
        )

    return {
        "project_id": str(project.id),
        "project_name": project.name,
        "summary": _project_budget_summary(project),
        "rooms": rooms_payload,
    }
