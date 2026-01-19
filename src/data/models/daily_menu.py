
from datetime import date

from sqlmodel import Field, Relationship, SQLModel

from data.models.products import Product


class DailyMenu(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    stock: int = Field(gt=0)
    menu_date: date = Field(index=True)

    product: Product | None = Relationship()
