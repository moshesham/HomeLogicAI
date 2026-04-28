from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from models.category import Category
    from models.decision import Decision


class Product(Base):
    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), index=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    retailer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(500))
    price: Mapped[float | None] = mapped_column(nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    images: Mapped[list[str]] = mapped_column(JSON, default=list)
    category_slug: Mapped[str] = mapped_column(String(120), index=True)
    attributes: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    raw_specs: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    user_notes: Mapped[str | None] = mapped_column(String, nullable=True)
    user_rating: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="researching")
    is_manual: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    category: Mapped[Category] = relationship(back_populates="products", foreign_keys=[category_id])
    decisions: Mapped[list[Decision]] = relationship(back_populates="product")

    def __repr__(self) -> str:
        return f"Product(id={self.id!s}, name={self.name!r}, status={self.status!r})"
