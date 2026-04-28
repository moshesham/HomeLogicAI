from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import get_db
from core.dependencies import get_current_user
from models.project import Project
from models.room import Room
from models.user import User
from schemas.room import RoomCreate, RoomResponse, RoomUpdate

router = APIRouter()


async def _get_user_room(db: AsyncSession, room_id: str, user_id: str) -> Room:
    try:
        rid = UUID(room_id)
        uid = UUID(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found") from exc

    result = await db.execute(
        select(Room)
        .join(Project, Project.id == Room.project_id)
        .where(Room.id == rid, Project.user_id == uid)
        .options(selectinload(Room.categories))
    )
    room = result.scalar_one_or_none()
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room


@router.get("/projects/{project_id}/rooms", response_model=list[RoomResponse])
async def list_rooms(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[RoomResponse]:
    try:
        pid = UUID(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from exc

    project_result = await db.execute(
        select(Project).where(Project.id == pid, Project.user_id == current_user.id)
    )
    if project_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    result = await db.execute(select(Room).where(Room.project_id == pid).order_by(Room.display_order, Room.created_at))
    rooms = result.scalars().all()
    return [
        RoomResponse.model_validate({**room.__dict__, "id": str(room.id), "project_id": str(room.project_id)})
        for room in rooms
    ]


@router.post("/projects/{project_id}/rooms", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    project_id: str,
    payload: RoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RoomResponse:
    try:
        pid = UUID(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from exc

    project_result = await db.execute(
        select(Project).where(Project.id == pid, Project.user_id == current_user.id)
    )
    if project_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    room = Room(project_id=pid, **payload.model_dump())
    db.add(room)
    await db.flush()
    return RoomResponse.model_validate({**room.__dict__, "id": str(room.id), "project_id": str(room.project_id)})


@router.get("/rooms/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RoomResponse:
    room = await _get_user_room(db, room_id, str(current_user.id))
    return RoomResponse.model_validate({**room.__dict__, "id": str(room.id), "project_id": str(room.project_id)})


@router.put("/rooms/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: str,
    payload: RoomUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RoomResponse:
    room = await _get_user_room(db, room_id, str(current_user.id))
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(room, field, value)
    await db.flush()
    return RoomResponse.model_validate({**room.__dict__, "id": str(room.id), "project_id": str(room.project_id)})


@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    room = await _get_user_room(db, room_id, str(current_user.id))
    await db.delete(room)
