from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from data.db.database import get_session
from data.dto.create_product_dto import CreateProductDTO
from data.dto.product_details_dto import ProductDetailsDTO
from data.repository.product_repository import ProductRepository
from services.product_service import ProductService

products_route = APIRouter(prefix="/products", tags=["products"])


def get_product_deps(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProductService:
    product_repo = ProductRepository(session)

    return ProductService(product_repo)


@products_route.post("/", response_model=ProductDetailsDTO)
async def create_product(
    product_data: CreateProductDTO,
    product_service: Annotated[ProductService, Depends(get_product_deps)],
) -> ProductDetailsDTO:
    """Crea un nuevo producto"""
    try:
        return await product_service.create_product(product_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@products_route.get("/{product_id}", response_model=ProductDetailsDTO)
async def get_product_by_id(
    product_id: int,
    product_service: Annotated[ProductService, Depends(get_product_deps)],
) -> ProductDetailsDTO:
    """Obtiene un producto por su ID interno"""
    try:
        return await product_service.get_product_by_id(product_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@products_route.get("/", response_model=list[ProductDetailsDTO])
async def list_all_products(
    product_service: Annotated[ProductService, Depends(get_product_deps)],
    only_available: bool = True,
) -> list[ProductDetailsDTO]:
    """Lista todos los productos"""
    try:
        return await product_service.get_all_products(only_available)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@products_route.get("/search/", response_model=list[ProductDetailsDTO])
async def search_products_by_name(
    name_query: str,
    product_service: Annotated[ProductService, Depends(get_product_deps)],
) -> list[ProductDetailsDTO]:
    """Busca productos por nombre"""
    try:
        return await product_service.search_by_name(name_query)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@products_route.patch("/{product_id}/availability", response_model=ProductDetailsDTO)
async def update_product_availability(
    product_id: int,
    available: bool,
    product_service: Annotated[ProductService, Depends(get_product_deps)],
) -> ProductDetailsDTO:
    """Actualiza la disponibilidad de un producto"""
    try:
        return await product_service.update_product_availability(product_id, available)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@products_route.put("/{product_id}", response_model=ProductDetailsDTO)
async def update_product_data(
    product_id: int,
    product_data: CreateProductDTO,
    product_service: Annotated[ProductService, Depends(get_product_deps)],
) -> ProductDetailsDTO:
    """Actualiza los datos de un producto existente"""
    try:
        return await product_service.update_product_data(product_id, product_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
