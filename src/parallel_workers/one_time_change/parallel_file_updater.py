import concurrent.futures
import json
import traceback
import logging
#logging.basicConfig(level=logging.DEBUG)
import requests

from scrappers.godsunchainedpoller import GodsUnchainedPoller
from util.custom_exceptions import TooManyAPICalls, Response_Error


class Parallel_File_Updater():

    def __init__(self):
        self._GodsUnchainedPoller = GodsUnchainedPoller()
        self._logger = logging.getLogger(__name__)

    def parallel_update_files(self, order_combination_list):
        amount_connections = len(order_combination_list)

        with concurrent.futures.ThreadPoolExecutor(max_workers=amount_connections) as executor:

            updated_orders = (executor.submit(self._download_newest_order, order_combination, amount_connections) for order_combination in order_combination_list)

            for updated_order in concurrent.futures.as_completed(updated_orders):

                try:
                    updated_order.result()

                except Exception as e:
                    raise

    def _download_newest_order(self, order_combination, amount_connections):
        get_type = order_combination[0]
        status = order_combination[1]

        try:
            self._GodsUnchainedPoller.download_order(get_type, status, amount_connections)
        except Exception as e:
            raise
