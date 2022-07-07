import concurrent.futures
from src.scrappers.godsunchainedpoller import GodsUnchainedPoller


class ParallelOrderDownloader:
    """
    A class to parallel download orders
    """

    def __init__(self):
        """
        The constructor of the ParallelOrderDownloader class
        """
        self._GodsUnchainedPoller = GodsUnchainedPoller()
        self._shut_down = False

    def parallel_download_timestamp_orders(self, get_type_str, status_str, time_stamp_str_list):
        """
        A method to parallel download orders based on a list of timestamps
        :param get_type_str: the type of order i.e. buy
        :param status_str: the status of the order i.e. active
        :param time_stamp_str_list: a list of timestamps to be downloaded
        :return: the result list
        """

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
        """
        A method to download one order based on a from- and to-timestamp
        :param get_type_str: the type of order to be downloaded
        :param status_str: the status of the order to be downloaded
        :param from_time_stamp_str: the from_timestamp
        :param to_time_stamp_str: the to_timestamp
        :return: the result
        """

        result = self._GodsUnchainedPoller.get_orders_based_on_timestamp(get_type_str, status_str, from_time_stamp_str, to_time_stamp_str)

        return (from_time_stamp_str, to_time_stamp_str, result)
