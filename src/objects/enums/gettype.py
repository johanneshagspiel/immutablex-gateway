from enum import Enum


class GetType(Enum):
    """
    An Enum class for the different type of requests that can be made i.e. get BUY orders or get a particular collection. .
    """
    BUY = 1
    SELL = 2
    COLLECTIONS = 3
    ALL_ASSETS = 4
