from pydantic import BaseModel, ConfigDict, Field


class CreateProductDTO(BaseModel):
    """DTO para crear un nuevo producto"""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Latte",
                    "description": "Café con leche",
                    "price": 2500,
                    "available": True,
                }
            ]
        }
    )

    name: str = Field(min_length=1, description="Nombre del producto")
    description: str = Field(min_length=1, description="Descripción del producto")
    price: int = Field(gt=0, description="Precio del producto en pesos chilenos")
    available: bool = Field(default=True, description="Disponibilidad del producto")
