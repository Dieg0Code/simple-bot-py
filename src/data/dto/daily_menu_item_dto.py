from datetime import date

from pydantic import BaseModel


class DailyMenuItemDTO(BaseModel):
    menu_id: int
    product_id: int
    product_name: str
    description: str | None
    price: int
    stock: int
    menu_date: date