from pydantic import BaseModel

from data.dto.order_item_detail_dto import OrderItemDetailDTO


class OrderDetailDTO(BaseModel):
    """Detalle completo de un pedido con sus items y productos"""

    order_id: int
    order_code: str
    customer_name: str
    customer_phone: str
    customer_address: str
    payment_method: str
    total_amount: int
    status: str
    items: list[OrderItemDetailDTO]
