import time
import traceback

import requests

from parallel_workers.parallel_order_id_downloader import Parallel_Order_ID_Downloader
from parallel_workers.parallel_order_by_sell_token_id_downloader import Parallel_Order_By_Sell_Token_ID_Downloader
from parallel_workers.parallel_order_downloader import Parallel_Order_Downloader
from parallel_workers.parallel_rank_downloader import Parallel_Rank_Downloader
from scrappers.gods_unchained_poller import Gods_Unchained_Poller
from util.custom_exceptions import Response_Error, Request_Error, TooManyAPICalls, Internal_Server_Error, \
    Start_New_Day_Error


class Parallel_List_Downloader():

    def __init__(self):
        self._operator = None


    def parallel_download_list(self, list_to_download, max_download_amount, task, additional_info_dic=None):

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

        if task == "get_inventory_orders_by_token_id":

            pobtid = Parallel_Order_By_Sell_Token_ID_Downloader()

            try:
                result = pobtid.parallel_download_orders_by_sell_token_id(to_process_list)

                prev_result_list.extend(result)
                return  prev_result_list

            except (Response_Error, Request_Error, TooManyAPICalls, Internal_Server_Error) as custom_errors:
                time.sleep(10)
                return self.execute_task(task, to_process_list, prev_result_list)



        elif task == "download_order_by_start_and_end_timestamp":

            parallel_order_downloader = Parallel_Order_Downloader("https://api.x.immutable.com/v1", "0xacb3c6a43d15b907e8433077b6d38ae40936fe2c", "Gods Unchained")

            try:
                result = parallel_order_downloader.parallel_download_timestamp_orders(get_type=additional_info_dic["get_type"], status=additional_info_dic["status"], time_stamp_str_list=to_process_list)

                prev_result_list.extend(result)
                return  prev_result_list

            except (Response_Error, Request_Error, TooManyAPICalls, Internal_Server_Error) as custom_errors:
                time.sleep(5)
                return self.execute_task(task, to_process_list, prev_result_list)


        elif task == "get_jsons_of_competition_by_order_id":

            poid = Parallel_Order_ID_Downloader()

            try:
                result = poid.parallel_download_orders_by_id(to_process_list, version="json")
                extracted_result_list = [entry[0] for entry in result]

                prev_result_list.extend(extracted_result_list)
                return prev_result_list

            except (Response_Error, Request_Error, TooManyAPICalls, Internal_Server_Error, requests.exceptions.ConnectionError) as custom_errors:
                time.sleep(2)
                return self.execute_task(task, to_process_list, prev_result_list)


        elif task == "download_rank_by_user_id":

            if len(prev_result_list) == 0:
                result_dic = {}

            elif len(prev_result_list) == 1:
                result_dic = prev_result_list.pop()
            else:
                raise Exception(f"How come the prev_result_list with length {len(prev_result_list)} and content {prev_result_list} exists?")

            parallel_rank_downloader = Parallel_Rank_Downloader()
            self._operator = parallel_rank_downloader

            try:
                new_result_dic = parallel_rank_downloader.parallel_download_rank(to_process_list)

                for user_id, rank in new_result_dic.items():
                    result_dic[user_id] = rank

                prev_result_list.append(result_dic)
                return prev_result_list

            except (Response_Error, Request_Error, TooManyAPICalls, Internal_Server_Error, Start_New_Day_Error) as custom_errors:
                raise custom_errors

            except Exception as e:
                print(type(e))
                print(e)
                traceback.print_exc()
                raise e


    def shut_down(self):
        self._operator._shut_down = True
