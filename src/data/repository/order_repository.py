import logging
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from data.dto.create_order_dto import CreateOrderDTO
from data.dto.order_detail_dto import OrderDetailDTO
from data.dto.order_item_detail_dto import OrderItemDetailDTO
from data.dto.update_order_items_dto import UpdateOrderItemsDTO
from data.models.order_items import OrderItems
from data.models.orders import Orders
from data.models.products import Product

logger = logging.getLogger(__name__)


class OrderRepositoryProtocol(Protocol):
    """Define el contrato para repositorios de pedidos"""

    async def create(self, order_data: CreateOrderDTO) -> Orders:
        """Crea un pedido con sus items"""
        ...

    async def get_by_id(self, order_id: int) -> Orders | None:
        """Obtiene un pedido por ID interno"""
        ...

    async def get_by_code(self, order_code: str) -> Orders | None:
        """Obtiene un pedido por código corto"""
        ...

    async def get_detail_by_code(self, order_code: str) -> OrderDetailDTO | None:
        """Obtiene el detalle completo de un pedido con productos"""
        ...

    async def update_status(self, order_code: str, new_status: str) -> Orders | None:
        """Actualiza el estado de un pedido"""
        ...

    async def update_items(
        self, order_code: str, update_data: UpdateOrderItemsDTO
    ) -> OrderDetailDTO | None:
        """Actualiza los items de un pedido (reemplaza todos)"""
        ...

    async def list_by_customer(
        self, customer_phone: str, limit: int = 3
    ) -> list[OrderDetailDTO]:
        """Lista todos los pedidos de un cliente"""
        ...

    async def delete(self, order_code: str) -> bool:
        """Elimina un pedido y sus items"""
        ...


class OrderRepository:
    """Repositorio para gestionar pedidos y sus items"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, order_data: CreateOrderDTO) -> OrderDetailDTO:
        """
        Crea un pedido con sus items.

        order_data: DTO con todos los datos del pedido validados
        """
        # Crear la orden
        order = Orders(
            customer_name=order_data.customer_name,
            customer_phone=order_data.customer_phone,
            customer_address=order_data.customer_address,
            payment_method=order_data.payment_method,
            total_amount=order_data.total_amount,
        )
        self.session.add(order)
        await self.session.flush()  # Para obtener el ID antes del commit
        logger.info("Creating order", extra={"order_id": order.id})

        # Crear los items del pedido
        for item in order_data.items:
            order_item = OrderItems(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_per_unit=item.price_per_unit,
            )
            self.session.add(order_item)

        await self.session.commit()
        await self.session.refresh(order)
        detail = await self.get_detail_by_code(order.order_code)
        if detail is None:
            raise ValueError(f"Failed to retrieve created order: {order.order_code}")
        return detail

    async def get_by_id(self, order_id: int) -> OrderDetailDTO | None:
        """Obtiene un pedido por su ID interno con sus items"""
        stmt = select(Orders).where(col(Orders.id) == order_id)
        result = await self.session.execute(stmt)
        order = result.scalar_one_or_none()
        if not order:
            return None
        if order.id is None:
            raise ValueError("Order ID not valid after database query")

        return await self.get_detail_by_code(order.order_code)

    async def get_by_code(self, order_code: str) -> OrderDetailDTO | None:
        """Obtiene un pedido por su código corto con sus items"""
        logger.debug("Getting order by code", extra={"order_code": order_code})
        stmt = select(Orders).where(col(Orders.order_code) == order_code)
        result = await self.session.execute(stmt)
        order = result.scalar_one_or_none()
        if not order:
            return None
        if order.id is None:
            raise ValueError("Order ID is invalid after database query")

        return await self.get_detail_by_code(order_code)

    async def get_detail_by_code(self, order_code: str) -> OrderDetailDTO | None:
        """Obtiene el detalle completo del pedido con información de productos"""
        logger.debug("Getting order detail", extra={"order_code": order_code})
        # Consulta para obtener la orden
        stmt_order = select(Orders).where(col(Orders.order_code) == order_code)
        result_order = await self.session.execute(stmt_order)
        order = result_order.scalar_one_or_none()

        if not order:
            logger.info("Order not found", extra={"order_code": order_code})
            return None

        if order.id is None:
            raise ValueError("Order ID is invalid after database query")

        # Consulta para obtener items con detalles de producto
        stmt_items = (
            select(
                col(OrderItems.product_id).label("product_id"),
                col(Product.name).label("product_name"),
                col(OrderItems.quantity).label("quantity"),
                col(OrderItems.price_per_unit).label("price_per_unit"),
                (col(OrderItems.quantity) * col(OrderItems.price_per_unit)).label(
                    "subtotal"
                ),
            )
            .join(Product, col(OrderItems.product_id) == col(Product.id))
            .where(col(OrderItems.order_id) == order.id)
        )
        result_items = await self.session.execute(stmt_items)

        # Construir DTOs de items
        items_dto = [OrderItemDetailDTO(**dict(row)) for row in result_items.mappings()]

        # Construir DTO completo
        return OrderDetailDTO(
            order_id=order.id,
            order_code=order.order_code,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            customer_address=order.customer_address,
            payment_method=order.payment_method,
            total_amount=order.total_amount,
            status=order.status,
            items=items_dto,
        )

    async def update_status(
        self, order_code: str, new_status: str
    ) -> OrderDetailDTO | None:
        """Actualiza el estado de un pedido"""
        logger.info(
            "Updating order status",
            extra={"order_code": order_code, "status": new_status},
        )
        order = await self.get_by_code(order_code)

        if order:
            order.status = new_status
            await self.session.commit()
            await self.session.refresh(order)
        return order

    async def update_items(
        self, update_data: UpdateOrderItemsDTO
    ) -> OrderDetailDTO | None:
        """Actualiza los items de un pedido (elimina los viejos y crea los nuevos)"""
        logger.info(
            "Updating order items", extra={"order_code": update_data.order_code}
        )
        order = await self.get_by_code(update_data.order_code)
        if not order:
            return None

        # Eliminar todos los items actuales
        stmt_delete = select(OrderItems).where(
            col(OrderItems.order_id) == order.order_id
        )
        result = await self.session.execute(stmt_delete)
        old_items = result.scalars().all()
        for item in old_items:
            await self.session.delete(item)

        # Crear los nuevos items y calcular el total
        total_amount = 0
        for item in update_data.items:
            order_item = OrderItems(
                order_id=order.order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_per_unit=item.price_per_unit,
            )
            self.session.add(order_item)
            total_amount += item.quantity * item.price_per_unit

        # Actualizar el total calculado
        order.total_amount = total_amount

        await self.session.commit()
        await self.session.refresh(order)

        # Devolver el detalle completo actualizado
        return await self.get_detail_by_code(update_data.order_code)

    async def list_by_customer(
        self, customer_phone: str, limit: int = 3
    ) -> list[OrderDetailDTO]:
        """Lista todos los pedidos de un cliente con sus detalles"""
        stmt = (
            select(Orders)
            .where(col(Orders.customer_phone) == customer_phone)
            .order_by(col(Orders.id).desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        orders = result.scalars().all()

        # Convertir cada orden a OrderDetailDTO
        order_details: list[OrderDetailDTO] = []
        for order in orders:
            if order.id is None:
                raise ValueError("Order ID is None after database query")

            # Consulta items para esta orden
            stmt_items = (
                select(
                    col(OrderItems.product_id).label("product_id"),
                    col(Product.name).label("product_name"),
                    col(OrderItems.quantity).label("quantity"),
                    col(OrderItems.price_per_unit).label("price_per_unit"),
                    (col(OrderItems.quantity) * col(OrderItems.price_per_unit)).label(
                        "subtotal"
                    ),
                )
                .join(Product, col(OrderItems.product_id) == col(Product.id))
                .where(col(OrderItems.order_id) == order.id)
            )
            result_items = await self.session.execute(stmt_items)

            items_dto = [
                OrderItemDetailDTO(**dict(row)) for row in result_items.mappings()
            ]

            order_details.append(
                OrderDetailDTO(
                    order_id=order.id,
                    order_code=order.order_code,
                    customer_name=order.customer_name,
                    customer_phone=order.customer_phone,
                    customer_address=order.customer_address,
                    payment_method=order.payment_method,
                    total_amount=order.total_amount,
                    status=order.status,
                    items=items_dto,
                )
            )

        return order_details

    async def delete(self, order_code: str) -> bool:
        """Elimina un pedido (los items se eliminan por CASCADE)"""
        logger.info("Deleting order", extra={"order_code": order_code})
        order = await self.get_by_code(order_code)

        if order:
            await self.session.delete(order)
            await self.session.commit()
            return True
        return False
