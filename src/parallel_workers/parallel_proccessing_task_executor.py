import concurrent.futures
import time
import traceback
from datetime import  datetime
from objects.enums.tasks import Processing_Task
from objects.orders.gods_unchained.order_administrator_gu import Order_Administrator_GU
from operators.error_handler import Error_Handler
from operators.processing_manager import Processing_Manager
from util.helpers import Future_Helper


class Parallel_Processing_Task_Executor():

    def __init__(self):
        self._processing_manager = Processing_Manager()


    def parallel_execute_processing_task(self, task_list):

        amount_tasks = len(task_list)

        Error_Handler.check_processing_logs()

        print(f"Loading Previous Active Updated DF")
        start_time = datetime.now()

        active_updated_orders_df = Order_Administrator_GU.create_active_updated_orders_df(get_type_string="SELL")
        print(f"t: {(datetime.now() - start_time).total_seconds()}")


        executor = concurrent.futures.ThreadPoolExecutor(max_workers=amount_tasks)
        future_list = []
        for task in task_list:
            temp_future = executor.submit(self._execute_processing_task, task, "SELL", active_updated_orders_df)
            future_list.append(temp_future)

        while Future_Helper.at_least_one_future_not_done(future_list):
            time.sleep(1)


    def _execute_processing_task(self, task, get_type, active_updated_orders_df):

        try:
            if task == Processing_Task.PROCESSING_NEW_DATA:
                self._processing_manager.processing_new_data(get_type=get_type, active_updated_orders_df=active_updated_orders_df)

        except Exception as e:
            print("#")
            print(type(e))
            print(e)
            self.shutdown()
            traceback.print_exc()
            print("#")


    def shutdown(self):
        self._processing_manager.shutdown()
