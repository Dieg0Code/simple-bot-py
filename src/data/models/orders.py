from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

from data.models.order_items import OrderItems
from utils.nanoid import generate_order_code


class Orders(SQLModel, table=True):
    """Modelo que representa un pedido realizado por un cliente."""

    id: int | None = Field(default=None, primary_key=True)
    order_code: str = Field(
        default_factory=generate_order_code,
        unique=True,
        index=True,
    )
    customer_name: str
    customer_phone: str
    customer_address: str
    payment_method: str
    total_amount: int
    status: str = Field(default="pending")

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

    items: list[OrderItems] = Relationship(back_populates="order")
