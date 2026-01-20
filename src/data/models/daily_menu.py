from datetime import date, datetime

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

from data.models.products import Product


class DailyMenu(SQLModel, table=True):
    """Modelo que representa el menú diario de productos disponibles."""

    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    stock: int = Field(gt=0)
    menu_date: date = Field(index=True)

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

    product: Product | None = Relationship()
