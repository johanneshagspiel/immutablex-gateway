import concurrent.futures
import json
import logging

import requests
import time

from scrappers.godsunchainedpoller import GodsUnchainedPoller
from scrappers.immutable_x_scrapper import Immutable_X_Scrapper
from util.custom_exceptions import TooManyAPICalls, Response_Error


class Parallel_Active_Orders_Checker():

    def __init__(self):
        self._gp = GodsUnchainedPoller()

    def parallel_download_timestamp_orders(self, order_id_list):
        connections = len(order_id_list)
        result = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=connections) as executor:
            future_to_url = (executor.submit(self._load_status, order_id) for order_id in order_id_list)

            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    data = future.result()
                    result.append(data)
                except Exception as e:
                    raise

        return result

    def _load_status(self, order_id):

        result = self._gp.get_order_by_order_id(order_id)
        status = result["status"]

        if status != "active":
            return order_id
        else:
            return None
