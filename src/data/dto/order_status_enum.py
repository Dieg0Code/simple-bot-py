from enum import Enum


class OrderStatusEnum(str, Enum):
    pending = "pending"
    in_process = "in_process"
    canceled = "canceled"
    delivered = "delivered"
