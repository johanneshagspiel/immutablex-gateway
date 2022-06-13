import time

from scrappers.gods_unchained_poller import Gods_Unchained_Poller
from util.custom_exceptions import Response_Error, Request_Error, TooManyAPICalls, Internal_Server_Error, \
    Start_New_Day_Error


class Safe_Gods_Unchained_Poller():

    def __init__(self):
        None

    @staticmethod
    def safe_download(task, information_dic):
        gp = Gods_Unchained_Poller()

        try:
            if task == "get_order_by_order_id":
                order_id = information_dic["order_id"]

                result = gp.get_order_by_order_id(order_id)

            elif task == "get_all_active_sell_orders_for_a_currency_and_quality":
                asset_name = information_dic["asset_name"]
                currency_string = information_dic["currency_string"]
                quality = information_dic["quality"]

                result = gp.get_all_active_sell_orders_for_a_currency_and_quality(asset_name=asset_name, currency_string=currency_string, quality=quality)


        except (Response_Error, Request_Error, TooManyAPICalls, Internal_Server_Error, Start_New_Day_Error) as custom_errors:
            time.sleep(5)
            return Safe_Gods_Unchained_Poller.safe_download(task, information_dic)

        return result