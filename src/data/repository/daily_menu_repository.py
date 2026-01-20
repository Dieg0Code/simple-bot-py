import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from data.dto.daily_menu_item_dto import DailyMenuItemDTO
from data.models.daily_menu import DailyMenu
from data.models.products import Product

logger = logging.getLogger(__name__)


class DailyMenuRepository:
    """Repositorio para gestionar el menú diario"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_available_by_date(self, menu_date: date) -> list[DailyMenuItemDTO]:
        """Obtiene productos disponibles evitando cargar el vector de embeddings"""
        logger.debug("Getting daily menu", extra={"menu_date": str(menu_date)})

        stmt = (
            select(
                col(DailyMenu.id).label("menu_id"),
                col(DailyMenu.product_id).label("product_id"),
                col(Product.name).label("product_name"),
                col(Product.description).label("description"),
                col(Product.price).label("price"),
                col(DailyMenu.stock).label("stock"),
                col(DailyMenu.menu_date).label("menu_date"),
            )
            .join(Product, col(DailyMenu.product_id) == col(Product.id))
            .where(
                col(DailyMenu.menu_date) == menu_date,
                col(DailyMenu.stock) > 0,
                col(Product.available),
            )
        )

        result = await self.session.execute(stmt)

        return [DailyMenuItemDTO(**dict(row)) for row in result.mappings()]

    async def create(
        self, product_id: int, stock: int, menu_date: date
    ) -> DailyMenuItemDTO:
        """Agrega un producto al menú diario"""
        logger.info(
            "Creating daily menu item",
            extra={"product_id": product_id, "menu_date": str(menu_date)},
        )
        menu_item = DailyMenu(product_id=product_id, stock=stock, menu_date=menu_date)
        self.session.add(menu_item)
        await self.session.commit()
        await self.session.refresh(menu_item)

        product_stmt = select(Product).where(col(Product.id) == menu_item.product_id)
        product_result = await self.session.execute(product_stmt)
        product = product_result.scalar_one_or_none()

        if not product:
            raise ValueError("Producto no encontrado para el item de menú creado")

        return DailyMenuItemDTO(
            menu_id=menu_item.id,
            product_id=menu_item.product_id,
            product_name=product.name,
            description=product.description,
            price=product.price,
            stock=menu_item.stock,
            menu_date=menu_item.menu_date,
        )

    async def update_stock(
        self, product_id: int, menu_date: date, new_stock: int
    ) -> DailyMenuItemDTO | None:
        """Actualiza el stock de un producto en el menú"""
        logger.info(
            "Updating daily menu stock",
            extra={
                "product_id": product_id,
                "menu_date": str(menu_date),
                "stock": new_stock,
            },
        )
        stmt = select(DailyMenu).where(
            col(DailyMenu.product_id) == product_id,
            col(DailyMenu.menu_date) == menu_date,
        )
        result = await self.session.execute(stmt)
        menu_item = result.scalar_one_or_none()

        if not menu_item:
            return None

        menu_item.stock = new_stock
        await self.session.commit()
        await self.session.refresh(menu_item)

        product_stmt = select(Product).where(col(Product.id) == menu_item.product_id)
        product_result = await self.session.execute(product_stmt)
        product = product_result.scalar_one_or_none()

        if not product:
            logger.error("Product not found for updated menu item")
            raise ValueError("Producto no encontrado para el item de menú actualizado")

        if menu_item.id is None:
            logger.error("Menu item ID is None after update")
            raise ValueError("El ID del item en None después de la actualización")

        return DailyMenuItemDTO(
            menu_id=menu_item.id,
            product_id=menu_item.product_id,
            product_name=product.name,
            description=product.description,
            price=product.price,
            stock=menu_item.stock,
            menu_date=menu_item.menu_date,
        )

    async def decrease_stock(
        self, product_id: int, menu_date: date, quantity: int
    ) -> DailyMenuItemDTO | None:
        """Reduce el stock (cuando se hace un pedido)"""
        logger.info(
            "Decreasing daily menu stock",
            extra={
                "product_id": product_id,
                "menu_date": str(menu_date),
                "quantity": quantity,
            },
        )
        stmt = select(DailyMenu).where(
            col(DailyMenu.product_id) == product_id,
            col(DailyMenu.menu_date) == menu_date,
        )
        result = await self.session.execute(stmt)
        menu_item = result.scalar_one_or_none()

        if not menu_item or menu_item.stock < quantity:
            return None

        menu_item.stock -= quantity
        await self.session.commit()
        await self.session.refresh(menu_item)

        product_stmt = select(Product).where(col(Product.id) == menu_item.product_id)
        product_result = await self.session.execute(product_stmt)
        product = product_result.scalar_one_or_none()

        if not product:
            logger.error("Product not found for decreased menu item")
            raise ValueError("Producto no encontrado para el item de menú actualizado")

        if menu_item.id is None:
            logger.error("Menu item ID is None after decrease")
            raise ValueError("El ID del item en None después de la actualización")

        return DailyMenuItemDTO(
            menu_id=menu_item.id,
            product_id=menu_item.product_id,
            product_name=product.name,
            description=product.description,
            price=product.price,
            stock=menu_item.stock,
            menu_date=menu_item.menu_date,
        )

    async def delete_menu_item(
        self, menu_id: int, item_id: int, menu_date: date
    ) -> bool:
        """Elimina un item del menú"""
        logger.info("Deleting daily menu item", extra={"menu_id": menu_id})
        stmt = select(DailyMenu).where(
            col(DailyMenu.id) == menu_id,
            col(DailyMenu.product_id) == item_id,
            col(DailyMenu.menu_date) == menu_date,
        )
        result = await self.session.execute(stmt)
        menu_item = result.scalar_one_or_none()

        if menu_item:
            await self.session.delete(menu_item)
            await self.session.commit()
            return True
        return False

    async def delete(self, menu_id: int) -> bool:
        """Elimina un item del menú"""
        logger.info("Deleting daily menu item", extra={"menu_id": menu_id})
        stmt = select(DailyMenu).where(col(DailyMenu.id) == menu_id)
        result = await self.session.execute(stmt)
        menu_item = result.scalar_one_or_none()

        if menu_item:
            await self.session.delete(menu_item)
            await self.session.commit()
            return True
        return False

    async def delete_by_date(self, menu_date: date) -> bool:
        """Elimina todos los items del menú de una fecha"""
        logger.info("Deleting daily menu items", extra={"menu_date": str(menu_date)})
        stmt = select(DailyMenu).where(col(DailyMenu.menu_date) == menu_date)
        result = await self.session.execute(stmt)
        menu_items = result.scalars().all()

        if menu_items:
            for item in menu_items:
                await self.session.delete(item)
            await self.session.commit()
            return True
        return False
