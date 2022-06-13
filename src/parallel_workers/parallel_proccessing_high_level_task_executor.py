import concurrent.futures
import sys
import time
import traceback
#logging.basicConfig(level=logging.DEBUG)

from objects.orders.gods_unchained.order_administrator_gu import Order_Administrator_GU
from objects.enums.tasks import Processing_Task, High_Level_Task, Download_Task
from operators.connection_manager import Connection_Manager
from operators.error_handler import Error_Handler
from parallel_workers.parallel_proccessing_task_executor import Parallel_Processing_Task_Executor
from parallel_workers.parallel_download_task_executor import Parallel_Download_Task_Executor
from util.custom_exceptions import TooManyAPICalls, Response_Error, Start_New_Day_Error, Request_Error, \
    Internal_Server_Error, Download_Log_Error
from util.helpers import Future_Helper


class Parallel_Processing_High_Level_Task_Executor():

    def __init__(self):
        self._parallel_download_task_executor = Parallel_Download_Task_Executor()
        self._parallel_download_task_executor.observer = self

        self._parallel_processing_task_executor = Parallel_Processing_Task_Executor()

        self._connection_manager = Connection_Manager(austria=False)
        self._error_handler = Error_Handler()

        self._wait_to_to_shutdown = True


    def run(self, mode):

        ### download_list ############################################################################################
        combined_download_task_list = [Download_Task.DOWN_ACTIVE_SELL_ORDERS, Download_Task.DOWN_FILLED_SELL_ORDERS, Download_Task.DOWN_CANCELLED_SELL_ORDERS,
                                       Download_Task.DOWN_ACTIVE_BUY_ORDERS, Download_Task.DOWN_FILLED_BUY_ORDERS, Download_Task.DOWN_CANCELLED_BUY_ORDERS,
                                       Download_Task.DOWN_MISSING_ORDERS
                                       ]
        sell_download_task_list = [Download_Task.DOWN_ACTIVE_SELL_ORDERS, Download_Task.DOWN_FILLED_SELL_ORDERS, Download_Task.DOWN_CANCELLED_SELL_ORDERS,
                                   Download_Task.DOWN_WIN_RATE]

        win_rate_list = [Download_Task.DOWN_WIN_RATE]
        double_checking_list = [Download_Task.DOWN_DOUBLE_CHECKING]
        missing_list = [Download_Task.DOWN_MISSING_ORDERS]

        test_1 = [Download_Task.DOWN_CANCELLED_BUY_ORDERS]
        test_2 = [Download_Task.DOWN_CANCELLED_BUY_ORDERS]

        ### process_list ##########################################################################################
        process_task_list = [Processing_Task.PROCESSING_NEW_DATA]

        if mode == "download":
            task_list = [(High_Level_Task.DOWNLOAD_TASK, sell_download_task_list)]
        elif mode == "process":
            task_list = [(High_Level_Task.PROCESS_TASK, process_task_list)]

        try:
            self.parallel_execute_high_level_task(task_list=task_list)

        except KeyboardInterrupt:
            print("Shutting down")
            self.shutdown()

            while self._wait_to_to_shutdown:
                time.sleep(1)

            sys.exit()

        except Exception as e:
            print("#")
            print(type(e))
            print(e)
            self.shutdown()
            traceback.print_exc()
            print("#")


    def parallel_execute_high_level_task(self, task_list):
        amount_tasks = len(task_list)

        high_level_task_list = [entry[0] for entry in task_list]

        if High_Level_Task.DOWNLOAD_TASK in high_level_task_list:

            print("Is Nordvpn on? Type yes to continue")

            answer = input()

            if answer == "yes":
                self._connection_manager.switch_ip(not_first_time=False)
            else:
                print("Nordvpn is not on - therefore the programme shuts down")
                sys.exit()


        executor = concurrent.futures.ThreadPoolExecutor(max_workers=amount_tasks)
        future_list = []
        for high_level, task_info_list in task_list:
            temp_future = executor.submit(self._execute_high_level_task, high_level, task_info_list)
            future_list.append(temp_future)

        while Future_Helper.at_least_one_future_not_done(future_list):
            time.sleep(1)


    def _execute_high_level_task(self, high_level_task, task_list):

        if high_level_task == High_Level_Task.DOWNLOAD_TASK:
            self._execute_download_task(task_list)

        elif high_level_task == High_Level_Task.PROCESS_TASK:
            self._execute_processing_task(task_list)


    def _execute_processing_task(self, task_list):
        self._parallel_processing_task_executor.parallel_execute_processing_task(task_list=task_list)


    def _execute_download_task(self, task_list):
        self._parallel_download_task_executor.parallel_execute_download_task(task_list=task_list)


    def inform(self, information, sender):

        print(f"Received {information} from {sender}")

        if isinstance(information, (Response_Error, Request_Error, TooManyAPICalls, Internal_Server_Error)):
            print(" ")
            print(information)
            self._connection_manager.switch_ip()
            self._parallel_download_task_executor.restart()

        elif isinstance(information, Start_New_Day_Error):
            print(" ")
            print(information)
            time.sleep(10)
            self._parallel_download_task_executor.restart()

        elif isinstance(information, Exception):
            traceback.print_exc()

        elif isinstance(information, str):
            if information == "shut_down_completed":
                self._wait_to_to_shutdown = False

    def shutdown(self):
        self._parallel_download_task_executor.shutdown()
        self._parallel_processing_task_executor.shutdown()