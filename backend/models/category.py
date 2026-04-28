from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from models.decision import Decision
    from models.product import Product
    from models.room import Room


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), index=True)
    category_slug: Mapped[str] = mapped_column(String(120), index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="researching")
    selected_product_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
    )
    budget_allocated: Mapped[float | None] = mapped_column(nullable=True)
    budget_actual: Mapped[float | None] = mapped_column(nullable=True)
    budget_estimated_low: Mapped[float | None] = mapped_column(nullable=True)
    budget_estimated_high: Mapped[float | None] = mapped_column(nullable=True)
    display_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    room: Mapped[Room] = relationship(back_populates="categories")
    products: Mapped[list[Product]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
        foreign_keys="Product.category_id",
    )
    selected_product: Mapped[Product | None] = relationship(
        foreign_keys=[selected_product_id],
        post_update=True,
    )
    decisions: Mapped[list[Decision]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Category(id={self.id!s}, slug={self.category_slug!r}, status={self.status!r})"
