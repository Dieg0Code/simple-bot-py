from datetime import date
from logging import Logger

from data.dto.daily_menu_item_dto import DailyMenuItemDTO
from data.repository.daily_menu_repository import DailyMenuRepository

logger: Logger = Logger(name=__name__)


class DailyMenuService:
    def __init__(self, daily_menu_repository: DailyMenuRepository) -> None:
        self.daily_menu_repository = daily_menu_repository

    async def get_available_menu(self, menu_date: date) -> list[DailyMenuItemDTO]:
        logger.debug(
            msg="Fetching available daily menu",
            extra={"menu_date": str(menu_date)},
        )

        if menu_date < date.today():
            logger.warning("Requested menu date %s is in the past", str(menu_date))
            return []

        return await self.daily_menu_repository.get_available_by_date(menu_date)

    async def add_menu_item(
        self, product_id: int, stock: int, menu_date: date
    ) -> DailyMenuItemDTO:
        logger.info(
            "Adding menu item",
            extra={
                "product_id": product_id,
                "stock": stock,
                "menu_date": str(menu_date),
            },
        )

        if stock <= 0:
            logger.error("Stock must be positive, received %d", stock)
            raise ValueError("Stock must be a positive integer")

        if menu_date < date.today():
            logger.error("Menu date %s is in the past", str(menu_date))
            raise ValueError("Menu date cannot be in the past")

        if product_id <= 0:
            logger.error("Product ID must be positive, received %d", product_id)
            raise ValueError("Product ID must be a positive integer")

        menu_item = await self.daily_menu_repository.create(
            product_id, stock, menu_date
        )

        return menu_item

    async def update_stock(
        self, menu_id: int, menu_date: date, new_stock: int
    ) -> DailyMenuItemDTO:
        logger.info(
            "Updating menu item stock",
            extra={"menu_id": menu_id, "new_stock": new_stock},
        )

        if new_stock < 0:
            logger.error("New stock cannot be negative, received %d", new_stock)
            raise ValueError("New stock cannot be negative")

        menu_item = await self.daily_menu_repository.update_stock(
            menu_id, menu_date, new_stock
        )

        if menu_item is None:
            logger.error(
                "Menu item not found for id %d and date %s", menu_id, str(menu_date)
            )
            raise ValueError(
                f"Menu item with id {menu_id} not found for date {menu_date}"
            )

        return menu_item

    async def decrease_stock(
        self, product_id: int, menu_date: date, quantity: int
    ) -> DailyMenuItemDTO:
        logger.info(
            "Decreasing menu item stock",
            extra={
                "product_id": product_id,
                "menu_date": str(menu_date),
                "quantity": quantity,
            },
        )

        if quantity <= 0:
            logger.error("Quantity to decrease must be positive, received %d", quantity)
            raise ValueError("Quantity to decrease must be a positive integer")

        menu_item = await self.daily_menu_repository.decrease_stock(
            product_id, menu_date, quantity
        )

        if menu_item is None:
            logger.error(
                "Menu item not found for product id %d and date %s",
                product_id,
                str(menu_date),
            )
            raise ValueError(
                f"Menu item with product id {product_id} not found for date {menu_date}"
            )

        return menu_item

    async def delete_menu_item(
        self, menu_id: int, item_id: int, menu_date: date
    ) -> bool:
        logger.info(
            "Deleting menu item",
            extra={"menu_id": menu_id, "item_id": item_id, "menu_date": str(menu_date)},
        )

        if menu_id <= 0 or item_id <= 0:
            logger.error(
                "Menu ID and Item ID must be positive, received menu_id=%d, item_id=%d",
                menu_id,
                item_id,
            )
            raise ValueError("Menu ID and Item ID must be positive integers")

        result = await self.daily_menu_repository.delete_menu_item(
            menu_id, item_id, menu_date
        )

        if not result:
            logger.warning(
                "Menu item with menu_id=%d, item_id=%d, date=%s not found for deletion",
                menu_id,
                item_id,
                str(menu_date),
            )

        return result

    async def delete_menu_by_id(self, menu_id: int) -> bool:
        logger.info("Deleting entire menu", extra={"menu_id": menu_id})

        if menu_id <= 0:
            logger.error("Menu ID must be positive, received %d", menu_id)
            raise ValueError("Menu ID must be a positive integer")

        result = await self.daily_menu_repository.delete(menu_id)

        if not result:
            logger.warning("Menu with id %d not found for deletion", menu_id)

        return result

    async def delete_menu_by_date(self, menu_date: date) -> bool:
        logger.info("Deleting menu by date", extra={"menu_date": str(menu_date)})

        if menu_date < date.today():
            logger.error("Menu date %s is in the past", str(menu_date))
            raise ValueError("Menu date cannot be in the past")

        result = await self.daily_menu_repository.delete_by_date(menu_date)

        if not result:
            logger.warning("No menu found for date %s to delete", str(menu_date))

        return result
