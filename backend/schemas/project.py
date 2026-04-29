from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from schemas.room import RoomSummaryResponse


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    address: str | None = None
    total_budget: float | None = None
    status: str = "active"
    start_date: date | None = None
    notes: str | None = None
    contacts: list[dict[str, Any]] = Field(default_factory=list)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    total_budget: float | None = None
    status: str | None = None
    start_date: date | None = None
    notes: str | None = None
    contacts: list[dict[str, Any]] | None = None


class ProjectSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    status: str


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime | None = None
    room_count: int | None = None
    budget_summary: dict[str, float | None] | None = None
    rooms: list[RoomSummaryResponse] = Field(default_factory=list)
