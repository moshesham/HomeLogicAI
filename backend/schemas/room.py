from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.category import CategorySummaryResponse


class RoomBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    room_budget: float | None = None
    notes: str | None = None
    display_order: int = 0


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    name: str | None = None
    room_budget: float | None = None
    notes: str | None = None
    display_order: int | None = None


class RoomSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    name: str
    display_order: int


class RoomResponse(RoomBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime | None = None
    categories: list[CategorySummaryResponse] = Field(default_factory=list)
