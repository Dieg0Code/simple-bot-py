from pydantic import BaseModel, Field


class ProductSearchResultDTO(BaseModel):
    """Resultado de búsqueda semántica de productos"""

    product_id: int = Field(gt=0, description="ID único del producto")
    name: str = Field(min_length=1, description="Nombre del producto")
    description: str | None = Field(
        default=None, description="Descripción del producto"
    )
    price: int = Field(gt=0, description="Precio del producto")
    available: bool = Field(description="Disponibilidad del producto")
    similarity_score: float = Field(
        ge=0.0, le=1.0, description="Puntuación de similitud (0.0 a 1.0)"
    )
