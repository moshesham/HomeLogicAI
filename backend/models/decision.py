from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from models.category import Category
    from models.product import Product


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
    )
    decision_type: Mapped[str] = mapped_column(String(50))
    rationale: Mapped[str] = mapped_column(String)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    category: Mapped[Category] = relationship(back_populates="decisions")
    product: Mapped[Product | None] = relationship(back_populates="decisions")

    def __repr__(self) -> str:
        return f"Decision(id={self.id!s}, type={self.decision_type!r}, category_id={self.category_id!s})"
