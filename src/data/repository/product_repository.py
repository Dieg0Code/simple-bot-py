import logging
from typing import Protocol

from pgvector.sqlalchemy import Vector
from sqlalchemy import desc, literal, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from data.dto.product_details_dto import ProductDetailsDTO
from data.dto.product_search_result_dto import ProductSearchResultDTO
from data.models.products import Product

logger = logging.getLogger(__name__)


class ProductRepositoryProtocol(Protocol):
    """Define el contrato para repositorios de productos"""

    async def get_by_id(self, product_id: int) -> ProductDetailsDTO | None:
        """Obtiene un producto por su ID interno"""
        ...

    async def list_all(self, only_available: bool = True) -> list[ProductDetailsDTO]:
        """Lista todos los productos"""
        ...

    async def search_by_name(self, name_query: str) -> list[ProductDetailsDTO]:
        """Busca productos por nombre (case insensitive)"""
        ...

    async def update_availability(
        self, product_id: int, available: bool
    ) -> ProductDetailsDTO | None:
        """Actualiza la disponibilidad de un producto"""
        ...

    async def update(self, product: Product) -> ProductDetailsDTO:
        """Actualiza los datos de un producto"""
        ...

    async def semantic_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        only_available: bool = True,
    ) -> list[ProductSearchResultDTO]:
        """Realiza búsqueda semántica usando vectores"""
        ...


class ProductRepository:
    """Repositorio para gestionar productos"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, product_id: int) -> ProductDetailsDTO | None:
        """Obtiene un producto por su ID (sin embedding)"""
        logger.debug("Getting product by id", extra={"product_id": product_id})
        stmt = select(
            col(Product.id).label("id"),
            col(Product.name).label("name"),
            col(Product.description).label("description"),
            col(Product.price).label("price"),
            col(Product.available).label("available"),
        ).where(col(Product.id) == product_id)

        result = await self.session.execute(stmt)
        row = result.mappings().one_or_none()

        if row:
            return ProductDetailsDTO(**dict(row))
        logger.info("Product not found", extra={"product_id": product_id})
        return None

    async def list_all(self, only_available: bool = True) -> list[ProductDetailsDTO]:
        """Lista todos los productos (sin embeddings)"""
        stmt = select(
            col(Product.id).label("id"),
            col(Product.name).label("name"),
            col(Product.description).label("description"),
            col(Product.price).label("price"),
            col(Product.available).label("available"),
        )

        if only_available:
            stmt = stmt.where(col(Product.available))

        result = await self.session.execute(stmt)

        return [ProductDetailsDTO(**dict(row)) for row in result.mappings()]

    async def search_by_name(self, name_query: str) -> list[ProductDetailsDTO]:
        """Busca productos por nombre (case insensitive, búsqueda parcial)"""
        stmt = select(
            col(Product.id).label("id"),
            col(Product.name).label("name"),
            col(Product.description).label("description"),
            col(Product.price).label("price"),
            col(Product.available).label("available"),
        ).where(
            col(Product.name).ilike(f"%{name_query}%"),
            col(Product.available),
        )

        result = await self.session.execute(stmt)

        return [ProductDetailsDTO(**dict(row)) for row in result.mappings()]

    async def update_availability(
        self, product_id: int, available: bool
    ) -> ProductDetailsDTO | None:
        """Actualiza la disponibilidad de un producto"""
        logger.info(
            "Updating product availability",
            extra={"product_id": product_id, "available": available},
        )
        stmt = select(Product).where(col(Product.id) == product_id)
        result = await self.session.execute(stmt)
        product = result.scalar_one_or_none()

        if not product:
            logger.info("Product not found", extra={"product_id": product_id})
            return None

        if product.id is None:
            raise ValueError("Product ID is invalid after database query")

        product.available = available
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)

        return ProductDetailsDTO(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            available=product.available,
        )

    async def update(self, product: Product) -> ProductDetailsDTO:
        """Actualiza los datos de un producto"""
        logger.info("Updating product", extra={"product_id": product.id})
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)

        if product.id is None:
            raise ValueError("Product ID is invalid after database update")

        return ProductDetailsDTO(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            available=product.available,
        )

    async def semantic_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        only_available: bool = True,
    ) -> list[ProductSearchResultDTO]:
        """Realiza búsqueda semántica usando vectores"""
        logger.debug(
            "Semantic search",
            extra={"top_k": top_k, "only_available": only_available},
        )
        stmt = select(
            col(Product.id).label("id"),
            col(Product.name).label("name"),
            col(Product.description).label("description"),
            col(Product.price).label("price"),
            col(Product.available).label("available"),
            (
                1
                - col(Product.embedding).op("<=>")(
                    literal(query_embedding, type_=Vector(768))
                )
            ).label("similarity_score"),
        )

        if only_available:
            stmt = stmt.where(col(Product.available))

        stmt = stmt.order_by(desc(col("similarity_score"))).limit(top_k)

        result = await self.session.execute(stmt)

        return [ProductSearchResultDTO(**dict(row)) for row in result.mappings()]
