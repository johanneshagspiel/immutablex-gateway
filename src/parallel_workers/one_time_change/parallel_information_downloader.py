import concurrent.futures
import json
import traceback
import logging
#logging.basicConfig(level=logging.DEBUG)
from scrappers.gods_unchained_poller import Gods_Unchained_Poller
from util.custom_exceptions import TooManyAPICalls, Response_Error


class Parallel_Information_downloader():

    def __init__(self):
        self._gods_unchained_poller = Gods_Unchained_Poller()
        self._logger = logging.getLogger(__name__)

    def parallel_download_information_for_old_orders(self, old_order_list):
        amount_connections = len(old_order_list)
        result_list = []
        encountered_error = False

        with concurrent.futures.ThreadPoolExecutor(max_workers=amount_connections) as executor:

            updated_orders = (executor.submit(self._download_information, old_order) for old_order in old_order_list)

            for updated_order in concurrent.futures.as_completed(updated_orders):
                try:
                    encountered_error_temp, old_order = updated_order.result()
                    result_list.append(old_order)

                    if encountered_error_temp == True:
                        encountered_error = True

                except Exception as exc:
                    print("??")

        return (result_list, encountered_error)

    def _download_information(self, old_order):

        encountered_error = False

        try:
            type = old_order.type
            result = self._gods_unchained_poller.get_order_by_order_id(old_order.order_id)

            if type == "sell":
                token_id = result["sell"]["data"]["token_id"]
                token_address = result["sell"]["data"]["id"]
            elif type == "buy":
                token_id = result["buy"]["data"]["token_id"]
                token_address = result["buy"]["data"]["id"]

            old_order.token_id = token_id
            old_order.token_address = token_address

        except Exception as exc:
            print(exc)
            encountered_error = True
        finally:
            return encountered_error, old_order

