from enum import Enum


class HighLevelTask(Enum):
    DOWNLOAD_TASK = 1
    PROCESS_TASK = 2


class DownloadTask(Enum):
    DOWN_ACTIVE_SELL_ORDERS = 1
    DOWN_FILLED_SELL_ORDERS = 2
    DOWN_CANCELLED_SELL_ORDERS = 3

    DOWN_ACTIVE_BUY_ORDERS = 4
    DOWN_FILLED_BUY_ORDERS = 5
    DOWN_CANCELLED_BUY_ORDERS = 6

    DOWN_WIN_RATE = 7
    DOWN_DOUBLE_CHECKING = 8
    DOWN_MISSING_ORDERS = 9

    DOWN_REQUEST_SCHEDULER = 10


class ProcessingTask(Enum):
    PROCESSING_NEW_DATA = 1
    WRITING_NEW_DATA = 2
