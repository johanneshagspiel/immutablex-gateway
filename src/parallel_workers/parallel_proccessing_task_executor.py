import concurrent.futures
import time
import traceback
from datetime import datetime
from src.objects.enums.tasks import ProcessingTask
from src.objects.orders.gods_unchained.orderadministratorgu import OrderAdministratorGU
from src.operators.errorhandler import ErrorHandler
from src.operators.processingmanager import ProcessingManager
from src.util.helpers import FutureHelper


class ParallelProcessingTaskExecutor:
    """
    A class to parallel execute processing tasks
    """

    def __init__(self):
        """
        The constructor for the ParallelProcessingTaskExecutor class
        """
        self._ProcessingManager = ProcessingManager()


    def parallel_execute_processing_task(self, task_list):
        """
        A method to parallel execute processing tasks
        :param task_list: a list of processing tasks to be executed
        :return: None
        """

        amount_tasks = len(task_list)

        ErrorHandler.check_processing_logs()

        print(f"Loading Previous Active Updated DF")
        start_time = datetime.now()

        active_updated_orders_df = OrderAdministratorGU.create_active_updated_orders_df(get_type_string="SELL")
        print(f"t: {(datetime.now() - start_time).total_seconds()}")

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=amount_tasks)
        future_list = []
        for task in task_list:
            temp_future = executor.submit(self._execute_processing_task, task, "SELL", active_updated_orders_df)
            future_list.append(temp_future)

        while FutureHelper.at_least_one_future_not_done(future_list):
            time.sleep(1)

    def _execute_processing_task(self, task, get_type, active_updated_orders_df):
        """
        A method to execute one processing task
        :param task: the processing task
        :param get_type: the type of order to be downloaded i.e. buy
        :param active_updated_orders_df: the active updated orders DataFrame
        :return: None
        """

        try:
            if task == ProcessingTask.PROCESSING_NEW_DATA:
                self._ProcessingManager.processing_new_data(get_type=get_type, active_updated_orders_df=active_updated_orders_df)

        except Exception as e:
            print("#")
            print(type(e))
            print(e)
            self.shutdown()
            traceback.print_exc()
            print("#")

    def shutdown(self):
        """
        A method to shutdown the ParallelProcessingTaskExecutor
        :return: None
        """
        self._ProcessingManager.shutdown()
