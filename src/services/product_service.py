from data.dto.create_product_dto import CreateProductDTO
from data.dto.product_details_dto import ProductDetailsDTO
from data.dto.product_search_result_dto import ProductSearchResultDTO
from data.dto.search_product_by_embedding_dto import SearchProductByEmbeddingDTO
from data.models.products import Product
from data.repository.product_repository import ProductRepository
from utils.embedder import new_embedder


class ProductService:
    def __init__(self, product_repository: ProductRepository) -> None:
        self.product_repository = product_repository
        self.embedder = new_embedder()

    async def create_product(self, product_data: CreateProductDTO) -> ProductDetailsDTO:
        """Crea un nuevo producto en la base de datos y retorna sus detalles"""

        if (
            not product_data.name
            or not product_data.description
            or product_data.price < 0
        ):
            raise ValueError("Invalid product data provided")

        product = Product(**product_data.model_dump())
        result = await self.embedder.embed_query(
            f"""
                # Nombre del producto: 
                    {product_data.name}
                # Descripción del producto:
                    {product_data.description}
            """
        )

        product.embedding = result.embeddings[0]

        new_product = await self.product_repository.create(product)

        return new_product

    async def get_product_by_id(self, product_id: int) -> ProductDetailsDTO | None:
        """Obtiene los detalles de un producto por su ID"""

        if product_id <= 0:
            raise ValueError("Product ID must be positive integer")

        product = await self.product_repository.get_by_id(product_id)

        if product is None:
            raise LookupError("Product not found")

        return product

    async def get_all_products(
        self, only_available: bool = True
    ) -> list[ProductDetailsDTO]:
        """Obtiene una lista de todos los productos, opcionalmente solo los disponibles"""

        return await self.product_repository.list_all(only_available)

    async def search_by_name(self, name_query: str) -> list[ProductDetailsDTO]:
        """Busca productos por nombre que coincidan con la consulta"""

        if not name_query.strip():
            raise ValueError("Name query must not be empty")

        return await self.product_repository.search_by_name(name_query)

    async def update_product_availability(
        self, product_id: int, available: bool
    ) -> ProductDetailsDTO:
        """Actualiza la disponibilidad de un producto"""

        if product_id <= 0:
            raise ValueError("Product ID must be a positive integer")

        updated_product = await self.product_repository.update_availability(
            product_id, available
        )

        if updated_product is None:
            raise LookupError("Product not found for availability update")

        return updated_product

    async def update_product_data(
        self, product_id: int, product_data: CreateProductDTO
    ) -> ProductDetailsDTO:
        """Actualiza los datos de un producto existente"""

        if product_id <= 0:
            raise ValueError("Product ID must be a positive integer")

        product = Product(id=product_id, **product_data.model_dump())
        updated_product = await self.product_repository.update(product)

        if updated_product is None:
            raise LookupError("Product not found for data update")

        return updated_product

    async def product_vector_search(
        self, search_query: SearchProductByEmbeddingDTO
    ) -> list[ProductSearchResultDTO]:
        """Realiza una búsqueda de productos basada en similitud de embeddings"""

        if not search_query.query_embedding:
            raise ValueError("Query embedding must not be empty")

        if search_query.top_k <= 0:
            raise ValueError("top_k must be a positive integer")

        products = await self.product_repository.semantic_search(
            query_embedding=search_query.query_embedding,
            top_k=search_query.top_k,
            only_available=search_query.only_available,
        )

        return products
