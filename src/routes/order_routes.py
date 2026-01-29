from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from data.db.database import get_session
from data.dto.create_order_dto import CreateOrderDTO
from data.dto.order_detail_dto import OrderDetailDTO
from data.dto.order_status_enum import OrderStatusEnum
from data.dto.update_order_items_dto import UpdateOrderItemsDTO
from data.repository.order_repository import OrderRepository
from services.order_service import OrderService

order_route = APIRouter(prefix="/orders", tags=["orders"])


def get_order_deps(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OrderService:
    """Proporciona las dependencias necesarias para OrderService"""
    order_repository = OrderRepository(session)
    return OrderService(order_repository)


@order_route.post(
    "/", response_model=OrderDetailDTO, status_code=status.HTTP_201_CREATED
)
async def create_order(
    order_data: Annotated[CreateOrderDTO, Body()],
    order_service: Annotated[OrderService, Depends(get_order_deps)],
) -> OrderDetailDTO:
    """Crea un nuevo pedido"""
    try:
        return await order_service.create_order(order_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@order_route.get(
    "/{order_id}", response_model=OrderDetailDTO, status_code=status.HTTP_200_OK
)
async def get_order_by_id(
    order_id: int,
    order_service: Annotated[OrderService, Depends(get_order_deps)],
) -> OrderDetailDTO:
    """Obtiene un pedido por su ID interno"""
    try:
        return await order_service.get_order_by_id(order_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@order_route.get(
    "/code/{order_code}", response_model=OrderDetailDTO, status_code=status.HTTP_200_OK
)
async def get_order_by_code(
    order_code: str,
    order_service: Annotated[OrderService, Depends(get_order_deps)],
) -> OrderDetailDTO:
    """Obtiene un pedido por su código interno"""
    try:
        return await order_service.get_order_by_code(order_code)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@order_route.get(
    "/detail/{order_code}",
    response_model=OrderDetailDTO,
    status_code=status.HTTP_200_OK,
)
async def get_order_detail_by_code(
    order_code: str,
    order_service: Annotated[OrderService, Depends(get_order_deps)],
) -> OrderDetailDTO:
    """Obtiene un detalle de pedido por su código interno"""
    try:
        return await order_service.get_order_detail_by_code(order_code)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@order_route.patch(
    "/{order_code}/status/",
    response_model=OrderDetailDTO,
    status_code=status.HTTP_200_OK,
)
async def update_order_status(
    order_code: str,
    new_status: Annotated[OrderStatusEnum, Query(min_length=1)],
    order_service: Annotated[OrderService, Depends(get_order_deps)],
) -> OrderDetailDTO:
    """Actualiza el estado de un pedido"""
    try:
        return await order_service.update_order_status(order_code, new_status)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@order_route.patch(
    "/items/", response_model=OrderDetailDTO, status_code=status.HTTP_200_OK
)
async def update_order_items(
    update_data: Annotated[UpdateOrderItemsDTO, Body()],
    order_service: Annotated[OrderService, Depends(get_order_deps)],
) -> OrderDetailDTO:
    """Actualiza los items de un pedido"""
    try:
        return await order_service.update_order_items(update_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@order_route.get(
    "/list/{customer_phone}",
    response_model=list[OrderDetailDTO],
    status_code=status.HTTP_200_OK,
)
async def get_orders_by_customer_phone(
    customer_phone: str,
    order_service: Annotated[OrderService, Depends(get_order_deps)],
) -> list[OrderDetailDTO]:
    """Obtiene una lista de pedidos por el teléfono del cliente"""
    try:
        return await order_service.list_orders_by_customer(customer_phone)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@order_route.delete("/{order_code}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_code: str,
    order_service: Annotated[OrderService, Depends(get_order_deps)],
) -> None:
    """Elimina un pedido por su código interno"""
    try:
        await order_service.delete_order(order_code)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    return None
