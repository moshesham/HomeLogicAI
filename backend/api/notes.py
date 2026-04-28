from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_user
from models.category import Category
from models.project import Project
from models.room import Room
from models.user import User
from services.storage_service import get_category_path, read_notes, write_notes

router = APIRouter()


class NotesPayload(BaseModel):
    content: str


async def _user_category_with_room_project(db: AsyncSession, category_id: str, user_id: str):
    try:
        cid = UUID(category_id)
        uid = UUID(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Category not found") from exc

    result = await db.execute(
        select(Category, Room, Project)
        .join(Room, Room.id == Category.room_id)
        .join(Project, Project.id == Room.project_id)
        .where(Category.id == cid, Project.user_id == uid)
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return row


@router.get("/categories/{category_id}/notes")
async def get_category_notes(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    category, room, project = await _user_category_with_room_project(db, category_id, str(current_user.id))
    category_path = get_category_path(str(project.id), str(room.id), str(category.id))
    return {"category_id": str(category.id), "content": read_notes(category_path)}


@router.put("/categories/{category_id}/notes")
async def put_category_notes(
    category_id: str,
    payload: NotesPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    category, room, project = await _user_category_with_room_project(db, category_id, str(current_user.id))
    category_path = get_category_path(str(project.id), str(room.id), str(category.id))
    write_notes(category_path, payload.content)
    return {"category_id": str(category.id), "content": payload.content}


@router.get("/projects/{project_id}/journal")
async def get_project_journal(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    try:
        pid = UUID(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc

    project_result = await db.execute(
        select(Project).where(Project.id == pid, Project.user_id == current_user.id)
    )
    project = project_result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(Category, Room)
        .join(Room, Room.id == Category.room_id)
        .where(Room.project_id == project.id)
    )

    entries: list[dict] = []
    for category, room in result.all():
        category_path = get_category_path(str(project.id), str(room.id), str(category.id))
        notes_content = read_notes(category_path)
        notes_file = category_path / "notes.md"
        if notes_content:
            updated_at = (
                datetime.fromtimestamp(notes_file.stat().st_mtime).isoformat() if notes_file.exists() else None
            )
            entries.append(
                {
                    "category_id": str(category.id),
                    "category_slug": category.category_slug,
                    "category_name": category.display_name,
                    "room_id": str(room.id),
                    "room_name": room.name,
                    "content": notes_content,
                    "updated_at": updated_at,
                }
            )

    entries.sort(key=lambda item: item["updated_at"] or "", reverse=True)
    return {"project_id": str(project.id), "entries": entries}
