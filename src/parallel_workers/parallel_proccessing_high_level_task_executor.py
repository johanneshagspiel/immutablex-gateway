import concurrent.futures
import sys
import time
import traceback
from src.objects.enums.tasks import ProcessingTask, HighLevelTask, DownloadTask
from src.operators.connectionmanager import ConnectionManager
from src.operators.errorhandler import ErrorHandler
from src.parallel_workers.parallel_proccessing_task_executor import ParallelProcessingTaskExecutor
from src.parallel_workers.paralleldownloadtaskexecutor import ParallelDownloadTaskExecutor
from src.util.custom_exceptions import TooManyAPICalls, ResponseError, StartNewDayError, RequestError, \
    InternalServerError
from src.util.helpers import FutureHelper


class ParallelProcessingHighLevelTaskExecutor:
    """
    A class to parallel execute high level tasks (download or process tasks)
    """

    def __init__(self):
        """
        The constructor of the ParallelProcessingHighLevelTaskExecutor
        """
        self._ParallelDownloadTaskExecutor = ParallelDownloadTaskExecutor()
        self._ParallelDownloadTaskExecutor.observer = self

        self._parallel_ProcessingTask_executor = ParallelProcessingTaskExecutor()

        self._ConnectionManager = ConnectionManager()
        self._ErrorHandler = ErrorHandler()

        self._wait_to_to_shutdown = True

    def run(self, task_list, mode):
        """
        A method to run a list of high level tasks
        :param mode: whether to execute download or processing tasks
        :return: None
        """

        if mode == "download":
            final_task_list = [(HighLevelTask.DOWNLOAD_TASK, task_list)]
        elif mode == "process":
            final_task_list = [(HighLevelTask.PROCESS_TASK, task_list)]

        try:
            self.parallel_execute_high_level_task(task_list=final_task_list)

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
        """
        A method to parallel execute high level tasks
        :param task_list: a list of high level tasks to be executed
        :return: None
        """
        amount_tasks = len(task_list)

        # HighLevelTask_list = [entry[0] for entry in task_list]
        #
        # if HighLevelTask.DOWNLOAD_TASK in HighLevelTask_list:
        #
        #     print("Is Nordvpn on? Type yes to continue")
        #
        #     answer = input()
        #
        #     if answer == "yes":
        #         self._ConnectionManager.switch_ip(not_first_time=False)
        #     else:
        #         print("Nordvpn is not on - therefore the programme shuts down")
        #         sys.exit()

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=amount_tasks)
        future_list = []
        for high_level, task_info_list in task_list:
            temp_future = executor.submit(self._execute_high_level_task, high_level, task_info_list)
            future_list.append(temp_future)

        while FutureHelper.at_least_one_future_not_done(future_list):
            time.sleep(1)

    def _execute_high_level_task(self, HighLevelTask, task_list):
        """
        A method to execute an high level task
        :param HighLevelTask:the high level task to be executed
        :param task_list: the tasks to be executed
        :return: None
        """

        if HighLevelTask == HighLevelTask.DOWNLOAD_TASK:
            self._execute_download_task(task_list)

        elif HighLevelTask == HighLevelTask.PROCESS_TASK:
            self._execute_processing_task(task_list)

    def _execute_processing_task(self, task_list):
        """
        A method to execute processing task
        :param task_list: a list of processing tasks to be executed
        :return: None
        """
        self._parallel_ProcessingTask_executor.parallel_execute_processing_task(task_list=task_list)

    def _execute_download_task(self, task_list):
        """
        A method to execute download task
        :param task_list: a list of download tasks to be executed
        :return: None
        """
        self._ParallelDownloadTaskExecutor.parallel_execute_download_task(task_list=task_list)

    def inform(self, information, sender):
        """
        A method to deal with received information
        :param information: the received information
        :param sender: the sender of the information
        :return: None
        """

        print(f"Received {information} from {sender}")

        if isinstance(information, (ResponseError, RequestError, TooManyAPICalls, InternalServerError)):
            print(" ")
            print(information)
            #self._ConnectionManager.switch_ip()
            self._ParallelDownloadTaskExecutor.restart()

        elif isinstance(information, StartNewDayError):
            print(" ")
            print(information)
            time.sleep(10)
            self._ParallelDownloadTaskExecutor.restart()

        elif isinstance(information, Exception):
            traceback.print_exc()

        elif isinstance(information, str):
            if information == "shut_down_completed":
                self._wait_to_to_shutdown = False

    def shutdown(self):
        """
        A method to shutdown the parallel high level task executor
        :return: None
        """
        self._ParallelDownloadTaskExecutor.shutdown()
        self._parallel_ProcessingTask_executor.shutdown()