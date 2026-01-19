from sqlmodel import Field, Relationship, SQLModel

from data.models.order_items import OrderItems
from utils.nanoid import generate_order_code


class Orders(SQLModel, table=True):

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

    items: list[OrderItems] = Relationship(back_populates="order")


