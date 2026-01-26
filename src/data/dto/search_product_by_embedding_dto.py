from pydantic import BaseModel, Field


class SearchProductByEmbeddingDTO(BaseModel):
    query_embedding: list[float] = Field(
        description="Embedding vector para la búsqueda semántica", default_factory=list
    )
    top_k: int = Field(
        default=5, gt=0, description="Número de productos similares a retornar"
    )
    only_available: bool = Field(
        default=True, description="Si es True, solo busca entre productos disponibles"
    )
