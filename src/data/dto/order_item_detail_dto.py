from pydantic import BaseModel


class OrderItemDetailDTO(BaseModel):
    """Detalle de un item de pedido con información del producto"""

    product_id: int
    product_name: str
    quantity: int
    price_per_unit: int
    subtotal: int  # quantity * price_per_unit
