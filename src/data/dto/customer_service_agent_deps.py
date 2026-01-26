from dataclasses import dataclass

from services.chat_service import ChatService
from services.order_service import OrderService
from services.product_service import ProductService


@dataclass
class CustomerServiceAgentDeps:
    product_service: ProductService
    chat_service: ChatService
    order_service: OrderService
