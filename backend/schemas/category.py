from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.decision import DecisionResponse
from schemas.product import ProductSummaryResponse


class CategoryBase(BaseModel):
    category_slug: str = Field(min_length=1, max_length=120)
    display_name: str = Field(min_length=1, max_length=255)
    status: str = "researching"
    selected_product_id: str | None = None
    budget_allocated: float | None = None
    budget_actual: float | None = None
    budget_estimated_low: float | None = None
    budget_estimated_high: float | None = None
    display_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    category_slug: str | None = None
    display_name: str | None = None
    status: str | None = None
    selected_product_id: str | None = None
    budget_allocated: float | None = None
    budget_actual: float | None = None
    budget_estimated_low: float | None = None
    budget_estimated_high: float | None = None
    display_order: int | None = None


class CategorySummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    room_id: str
    category_slug: str
    display_name: str
    status: str


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    room_id: str
    created_at: datetime
    updated_at: datetime | None = None
    products: list[ProductSummaryResponse] = Field(default_factory=list)
    decisions: list[DecisionResponse] = Field(default_factory=list)
