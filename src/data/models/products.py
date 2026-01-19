from pgvector.sqlalchemy import Vector
from sqlmodel import Column, Field, Relationship, SQLModel

from data.models.orders import OrderItems


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(index=True, unique=True)
    description: str | None = None
    price: int = Field(gt=0)
    available: bool = Field(default=True)

    embedding: list[float] = Field(sa_column=Column(Vector(768)))
    order_items: list[OrderItems] = Relationship(back_populates="product")
