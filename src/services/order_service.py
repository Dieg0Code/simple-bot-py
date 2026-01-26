from logging import Logger

from data.dto.create_order_dto import CreateOrderDTO
from data.dto.order_detail_dto import OrderDetailDTO
from data.dto.update_order_items_dto import UpdateOrderItemsDTO
from data.repository.order_repository import OrderRepository

logger: Logger = Logger(name=__name__)


class OrderService:
    def __init__(self, order_repository: OrderRepository) -> None:
        self.order_repository = order_repository

    async def create_order(self, order_data: CreateOrderDTO) -> OrderDetailDTO:
        """Crea un nuevo pedido"""

        if not order_data.items:
            logger.error("Order must contain at least one item")
            raise ValueError("Order must contain at least one item")

        logger.info(
            "Creating new order",
            extra={
                "customer_name": order_data.customer_name,
                "total_amount": order_data.total_amount,
                "item_count": len(order_data.items),
            },
        )

        return await self.order_repository.create(order_data)

    async def get_order_by_id(self, order_id: int) -> OrderDetailDTO | None:
        """Obtiene un pedido por su ID interno"""

        logger.debug("Fetching order by ID", extra={"order_id": order_id})

        if order_id <= 0:
            logger.error("Order ID must be positive, received %d", order_id)
            raise ValueError("Order ID must be a positive integer")

        order = await self.order_repository.get_by_id(order_id)

        if order is None:
            logger.warning(" Order not found", extra={"order_id": order_id})
            raise LookupError(f"Order with ID {order_id} not found")
        return order

    async def get_order_by_code(self, order_code: str) -> OrderDetailDTO | None:
        """Obtiene un pedido por su código interno"""

        logger.debug("Fetching order by code", extra={"order_code": order_code})

        if not order_code.strip():
            logger.error("Order code cannot be empty string")
            raise ValueError("Order code cannot be empty string")

        order = await self.order_repository.get_by_code(order_code)

        if order is None:
            logger.warning("Order not found", extra={"order_code": order_code})
            raise LookupError(f"Order with code {order_code} not found")
        return order

    async def get_order_detail_by_code(self, order_code: str) -> OrderDetailDTO | None:
        """Obtiene un detalle de pedido por su código interno"""

        logger.debug("Fetching order detail by code", extra={"order_code": order_code})

        if not order_code.strip():
            logger.error("Order code must not be empty")
            raise ValueError("Order code must not be empty")

        order = await self.order_repository.get_detail_by_code(order_code)

        if order is None:
            logger.warning("Order not found", extra={"order_code": order_code})
            raise LookupError(f"Order with code {order_code} not found")
        return order

    async def update_order_status(
        self, order_code: str, new_status: str
    ) -> OrderDetailDTO | None:
        """Actualiza el estado de un pedido"""

        logger.info(
            "Updating order status",
            extra={"order_code": order_code, "new_status": new_status},
        )

        if not order_code.strip():
            logger.error("invalid order code")
            raise ValueError("Order code must be a valid non-empty string")

        if not new_status.strip():
            logger.error("New status cannot be empty")
            raise ValueError("New status cannot be empty")

        order = await self.order_repository.update_status(order_code, new_status)

        if order is None:
            logger.warning(
                "Order not found for status update", extra={"order_code": order_code}
            )
            raise LookupError(
                f"Order with code {order_code} not found for status update"
            )
        return order

    async def update_order_items(
        self, update_data: UpdateOrderItemsDTO
    ) -> OrderDetailDTO | None:
        """Actualiza los items de un pedido"""

        logger.info(
            "Updating order items",
            extra={
                "order_code": update_data.order_code,
                "new_item_count": len(update_data.items),
            },
        )

        if not update_data.order_code.strip():
            logger.error("Invalid order code")
            raise ValueError("Order code must be a valid non-empty string")

        if not update_data.items:
            logger.error("Order must have at least one item")
            raise ValueError("Order must have at least one item")

        order = await self.order_repository.update_items(update_data)

        if order is None:
            logger.warning(
                "Order not found for item update",
                extra={"order_code": update_data.order_code},
            )
            raise LookupError(
                f"Order with code {update_data.order_code} not found for item update"
            )

        return order

    async def list_orders_by_customer(
        self, customer_phone: str
    ) -> list[OrderDetailDTO]:
        """Lista los pedidos realizados por un cliente específico en base a su teléfono"""

        logger.debug(
            "Listing orders by customer",
            extra={"customer_phone": customer_phone},
        )

        if not customer_phone.strip():
            logger.error("Customer phone number cannot be empty")
            raise ValueError("Customer phone number cannot be empty")

        return await self.order_repository.list_by_customer(customer_phone)

    async def delete_order(self, order_code: str) -> bool:
        """Elimina un pedido por su código interno"""

        logger.info("Deleting order", extra={"order_code": order_code})

        if not order_code.strip():
            logger.error("Order code cannot be empty")
            raise ValueError("Order code cannot be empty")

        return await self.order_repository.delete(order_code)
