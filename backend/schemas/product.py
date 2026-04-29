from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    source_url: str | None = None
    retailer: str | None = None
    name: str = Field(min_length=1, max_length=500)
    price: float | None = None
    currency: str = "USD"
    images: list[str] = Field(default_factory=list)
    category_slug: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    raw_specs: dict[str, Any] = Field(default_factory=dict)
    scraped_at: datetime | None = None
    user_notes: str | None = None
    user_rating: int | None = Field(default=None, ge=1, le=5)
    status: str = "researching"
    is_manual: bool = False


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    source_url: str | None = None
    retailer: str | None = None
    name: str | None = None
    price: float | None = None
    currency: str | None = None
    images: list[str] | None = None
    category_slug: str | None = None
    attributes: dict[str, Any] | None = None
    raw_specs: dict[str, Any] | None = None
    scraped_at: datetime | None = None
    user_notes: str | None = None
    user_rating: int | None = Field(default=None, ge=1, le=5)
    status: str | None = None
    is_manual: bool | None = None


class ProductSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    status: str
    price: float | None = None
    currency: str = "USD"


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    category_id: str
    created_at: datetime
    updated_at: datetime | None = None
