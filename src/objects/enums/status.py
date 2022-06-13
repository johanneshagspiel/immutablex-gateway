from enum import Enum


class Status(Enum):
    ACTIVE = 1
    CANCELLED = 2
    EXPIRED = 3
    FILLED = 4
    INACTIVE = 5
