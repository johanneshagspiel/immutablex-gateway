from enum import Enum


class Status(Enum):
    """
    An Enum class representing the different statuses that an order can be in.
    """
    ACTIVE = 1
    CANCELLED = 2
    EXPIRED = 3
    FILLED = 4
    INACTIVE = 5
