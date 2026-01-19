from pydantic import BaseModel, Field


class CreateOrderItemDTO(BaseModel):
    """Item individual para crear un pedido"""

    product_id: int = Field(gt=0, description="ID del producto a ordenar")
    quantity: int = Field(gt=0, description="Cantidad de unidades del producto")
    price_per_unit: int = Field(gt=0, description="Precio por unidad del producto")


class CreateOrderDTO(BaseModel):
    """Datos necesarios para crear un nuevo pedido de comida"""

    customer_name: str = Field(min_length=1, description="Nombre completo del cliente")
    customer_phone: str = Field(
        min_length=1, description="Número de teléfono del cliente"
    )
    customer_address: str = Field(
        min_length=1, description="Dirección de entrega del pedido"
    )
    payment_method: str = Field(
        min_length=1,
        description="Método de pago (efectivo, tarjeta, transferencia)",
        pattern="^(efectivo|tarjeta|transferencia)$",
    )
    total_amount: int = Field(
        gt=0, description="Monto total del pedido en pesos chilenos"
    )
    items: list[CreateOrderItemDTO] = Field(
        min_length=1, description="Lista de productos incluidos en el pedido"
    )
