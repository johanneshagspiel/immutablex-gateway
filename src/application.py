from src.objects.enums.tasks import DownloadTask, ProcessingTask
from src.operators.helpers.currency_helper import CurrencyHelper
from src.parallel_workers.parallel_proccessing_high_level_task_executor import ParallelProcessingHighLevelTaskExecutor


class Application:
    """
    A class that represents the application.
    """

    def __init__(self):
        """
        The constructor of the Application class
        """
        self.start_up()

    def start_up(self):
        """
        A method called when an instance of an Application is created the first time.
        :return: None
        """
        currency_helper = CurrencyHelper()

        new_currency_boolean, not_implemented_string = currency_helper.check_for_new_currencies()

        if not new_currency_boolean:
            raise NotImplementedError(not_implemented_string)

    def run(self):
        """
        A method to run the main loop of the application
        :return: None
        """

        combined_DownloadTask_list = [DownloadTask.DOWN_ACTIVE_SELL_ORDERS, DownloadTask.DOWN_FILLED_SELL_ORDERS, DownloadTask.DOWN_CANCELLED_SELL_ORDERS,
                                       DownloadTask.DOWN_ACTIVE_BUY_ORDERS, DownloadTask.DOWN_FILLED_BUY_ORDERS, DownloadTask.DOWN_CANCELLED_BUY_ORDERS]

        sell_DownloadTask_list = [DownloadTask.DOWN_ACTIVE_SELL_ORDERS, DownloadTask.DOWN_FILLED_SELL_ORDERS, DownloadTask.DOWN_CANCELLED_SELL_ORDERS,]

        win_rate_list = [DownloadTask.DOWN_WIN_RATE]
        double_checking_list = [DownloadTask.DOWN_DOUBLE_CHECKING]
        missing_list = [DownloadTask.DOWN_MISSING_ORDERS]

        test_1 = [DownloadTask.DOWN_REQUEST_SCHEDULER, DownloadTask.DOWN_FILLED_SELL_ORDERS]
        test_2 = [DownloadTask.DOWN_CANCELLED_BUY_ORDERS]

        process_task_list = [ProcessingTask.PROCESSING_NEW_DATA]

        executor = ParallelProcessingHighLevelTaskExecutor()
        executor.run(sell_DownloadTask_list, "download")
