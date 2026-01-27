from pydantic import BaseModel, ConfigDict, Field

from datetime import date


class DailyMenuItemDTO(BaseModel):
    """DTO para un ítem del menú diario"""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "menu_id": 1,
                    "product_id": 101,
                    "product_name": "Empanada de Pino",
                    "description": "Empanada tradicional chilena rellena de carne, cebolla y huevo.",
                    "price": 1800,
                    "stock": 25,
                    "menu_date": "2026-01-26",
                }
            ]
        }
    )

    menu_id: int = Field(description="ID del menú diario")
    product_id: int = Field(description="ID del producto")
    product_name: str = Field(description="Nombre del producto")
    description: str | None = Field(
        default=None, description="Descripción del producto"
    )
    price: int = Field(description="Precio del producto en pesos chilenos")
    stock: int = Field(description="Stock disponible para el día")
    menu_date: date = Field(description="Fecha del menú diario (YYYY-MM-DD)")
