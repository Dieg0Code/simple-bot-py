from pydantic import BaseModel


class ProductDetailsDTO(BaseModel):
    id: int
    name: str
    description: str | None
    price: int
    available: bool
