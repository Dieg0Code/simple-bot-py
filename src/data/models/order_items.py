from sqlmodel import Field, Relationship, SQLModel

from data.models.orders import Orders
from data.models.products import Product


class OrderItems(SQLModel, table=True):
    """Modelo que representa los items de un pedido."""

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(gt=0)
    price_per_unit: int = Field(gt=0)

    order: Orders | None = Relationship(back_populates="items")
    product: Product | None = Relationship(back_populates="order_items")
