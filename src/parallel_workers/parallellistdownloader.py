import time
import traceback
import requests
from src.parallel_workers.parallelorderiddownloader import ParallelOrderIDDownloader
from src.parallel_workers.parallelorderbyselltokeniddownloader import ParallelOrderBySellTokenIDDownloader
from src.parallel_workers.parallelorderdownloader import ParallelOrderDownloader
from src.parallel_workers.parallelrankdownloader import ParallelRankDownloader
from src.util.custom_exceptions import ResponseError, RequestError, TooManyAPICalls, InternalServerError, \
    StartNewDayError


class ParallelListDownloader:
    """
    A class to parallel download a list of items
    """

    def __init__(self):
        """
        The constructor of the ParallelListDownloader class
        """
        self._operator = None

    def parallel_download_list(self, list_to_download, max_download_amount, task, additional_info_dic=None):
        """
        A method to parallel download a list of item
        :param list_to_download: a list of items to be downloaded
        :param max_download_amount: the maximum amount of items to be downloaded in parallel
        :param task: the kind of information to be downloaded
        :param additional_info_dic: additional information to download items in the form of a dictionary
        :return: the result list
        """

        result_list = []

        check_more = True
        start_position = 0

        if len(list_to_download) > max_download_amount:
            end_position = max_download_amount
        else:
            end_position = len(list_to_download)

        while check_more:

            if end_position == len(list_to_download):
                check_more = False

            next_portion_check = list_to_download[start_position:end_position]

            if len(next_portion_check) > 0:

                result_list = self.execute_task(task, next_portion_check, result_list, additional_info_dic)

                if len(list_to_download) < (end_position + max_download_amount):
                    start_position = end_position
                    end_position = len(list_to_download)
                else:
                    start_position = end_position
                    end_position = end_position + max_download_amount
            else:
                check_more = False

        return result_list

    def execute_task(self, task, to_process_list, prev_result_list, additional_info_dic=None):
        """
        A method to download one kind of item
        :param task: the kind of information to be downloaded
        :param to_process_list: the list to be downloaded
        :param prev_result_list: the list of previous results
        :param additional_info_dic: additional information in the form of a dictionary
        :return: None
        """

        if task == "get_inventory_orders_by_token_id":

            pobtid = ParallelOrderBySellTokenIDDownloader()

            try:
                result = pobtid.parallel_download_orders_by_sell_token_id(to_process_list)

                prev_result_list.extend(result)
                return  prev_result_list

            except (ResponseError, RequestError, TooManyAPICalls, InternalServerError) as custom_errors:
                time.sleep(10)
                return self.execute_task(task, to_process_list, prev_result_list)

        elif task == "download_order_by_start_and_end_timestamp":

            parallel_order_downloader = ParallelOrderDownloader("https://api.x.immutable.com/v1", "0xacb3c6a43d15b907e8433077b6d38ae40936fe2c", "Gods Unchained")

            try:
                result = parallel_order_downloader.parallel_download_timestamp_orders(get_type=additional_info_dic["get_type"], status=additional_info_dic["status"], time_stamp_str_list=to_process_list)

                prev_result_list.extend(result)
                return  prev_result_list

            except (ResponseError, RequestError, TooManyAPICalls, InternalServerError) as custom_errors:
                time.sleep(5)
                return self.execute_task(task, to_process_list, prev_result_list)

        elif task == "get_jsons_of_competition_by_order_id":

            poid = ParallelOrderIDDownloader()

            try:
                result = poid.parallel_download_orders_by_id(to_process_list, version="json")
                extracted_result_list = [entry[0] for entry in result]

                prev_result_list.extend(extracted_result_list)
                return prev_result_list

            except (ResponseError, RequestError, TooManyAPICalls, InternalServerError, requests.exceptions.ConnectionError) as custom_errors:
                time.sleep(2)
                return self.execute_task(task, to_process_list, prev_result_list)

        elif task == "download_rank_by_user_id":

            if len(prev_result_list) == 0:
                result_dic = {}

            elif len(prev_result_list) == 1:
                result_dic = prev_result_list.pop()
            else:
                raise Exception(f"How come the prev_result_list with length {len(prev_result_list)} and content {prev_result_list} exists?")

            parallel_rank_downloader = ParallelRankDownloader()
            self._operator = parallel_rank_downloader

            try:
                new_result_dic = parallel_rank_downloader.parallel_download_rank(to_process_list)

                for user_id, rank in new_result_dic.items():
                    result_dic[user_id] = rank

                prev_result_list.append(result_dic)
                return prev_result_list

            except (ResponseError, RequestError, TooManyAPICalls, InternalServerError, StartNewDayError) as custom_errors:
                raise custom_errors

            except Exception as e:
                print(type(e))
                print(e)
                traceback.print_exc()
                raise e

    def shut_down(self):
        """
        A method to shut down the parallel download process
        :return: None
        """
        self._operator._shut_down = True
