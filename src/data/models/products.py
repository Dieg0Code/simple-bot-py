from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, func
from sqlmodel import Column, Field, Relationship, SQLModel

from data.models.orders import OrderItems


class Product(SQLModel, table=True):
    """Modelo que representa un producto disponible para la venta."""

    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(index=True, unique=True)
    description: str | None = None
    price: int = Field(gt=0)
    available: bool = Field(default=True)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        )
    )

    embedding: list[float] = Field(sa_column=Column(Vector(768)))
    order_items: list[OrderItems] = Relationship(back_populates="product")
