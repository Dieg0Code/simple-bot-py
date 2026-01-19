from pydantic import BaseModel, Field

from data.dto.create_order_dto import CreateOrderItemDTO


class UpdateOrderItemsDTO(BaseModel):
    """DTO para actualizar los items de un pedido existente"""

    order_code: str = Field(
        min_length=6, description="Código único del pedido a actualizar"
    )
    items: list[CreateOrderItemDTO] = Field(
        min_length=1, description="Lista actualizada de productos en el pedido"
    )
