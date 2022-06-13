import concurrent.futures
import logging
from scrappers.gods_unchained_poller import Gods_Unchained_Poller


class Parallel_Order_Downloader():

    def __init__(self):
        self._gods_unchained_poller = Gods_Unchained_Poller()
        self._shut_down = False

    def parallel_download_timestamp_orders(self, get_type_str, status_str, time_stamp_str_list):

        connections = len(time_stamp_str_list)
        result = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=connections) as executor:
            future_to_url = (executor.submit(self._load_url, get_type_str, status_str, from_time_stamp_str, to_time_stamp_str) for (from_time_stamp_str, to_time_stamp_str) in time_stamp_str_list)
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    data = future.result()
                    result.append(data)
                except Exception as e:
                    raise

                if self._shut_down:
                    executor.shutdown(wait=False, cancel_futures=True)

        return result



    def _load_url(self, get_type_str, status_str, from_time_stamp_str, to_time_stamp_str):

        result = self._gods_unchained_poller.get_orders_based_on_timestamp(get_type_str, status_str, from_time_stamp_str, to_time_stamp_str)

        return (from_time_stamp_str, to_time_stamp_str, result)
