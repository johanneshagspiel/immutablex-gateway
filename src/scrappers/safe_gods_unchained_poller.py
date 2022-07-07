import time
from src.scrappers.godsunchainedpoller import GodsUnchainedPoller
from src.util.custom_exceptions import ResponseError, RequestError, TooManyAPICalls, InternalServerError, \
    StartNewDayError


class SafeGodsUnchainedPoller:
    """
    A class to make exception safe requests to the IMX api
    """

    def __init__(self):
        """
        The constructor of the SafeGodsUnchainedPoller class
        """
        pass

    @staticmethod
    def safe_download(task, information_dic):
        """
        A method to safe download information
        :param task: information to be downloaded
        :param information_dic: additional information dictionary
        :return: result
        """
        gp = GodsUnchainedPoller()

        try:
            if task == "get_order_by_order_id":
                order_id = information_dic["order_id"]

                result = gp.get_order_by_order_id(order_id)

            elif task == "get_all_active_sell_orders_for_a_currency_and_quality":
                asset_name = information_dic["asset_name"]
                currency_string = information_dic["currency_string"]
                quality = information_dic["quality"]

                result = gp.get_all_active_sell_orders_for_a_currency_and_quality(asset_name=asset_name, currency_string=currency_string, quality=quality)

        except (ResponseError, RequestError, TooManyAPICalls, InternalServerError, StartNewDayError):
            time.sleep(5)
            return SafeGodsUnchainedPoller.safe_download(task, information_dic)

        return result
