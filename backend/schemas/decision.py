from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DecisionBase(BaseModel):
    product_id: str | None = None
    decision_type: str = Field(min_length=1, max_length=50)
    rationale: str = Field(min_length=1)
    source: str | None = None


class DecisionCreate(DecisionBase):
    pass


class DecisionUpdate(BaseModel):
    product_id: str | None = None
    decision_type: str | None = None
    rationale: str | None = None
    source: str | None = None


class DecisionResponse(DecisionBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    category_id: str
    created_at: datetime
