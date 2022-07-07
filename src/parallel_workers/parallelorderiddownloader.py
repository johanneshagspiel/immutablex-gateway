import concurrent.futures
from src.scrappers.godsunchainedpoller import GodsUnchainedPoller


class ParallelOrderIDDownloader:
    """
    A class to parallel download orders by id
    """

    def __init__(self):
        """
        The constructor of the ParallelOrderIDDownloader class
        """
        self._GodsUnchainedPoller = GodsUnchainedPoller()
        self._shut_down = False

    def parallel_download_orders_by_id(self, missing_order_id_list, version):
        """
        A method to parallel download orders by id
        :param missing_order_id_list: a list of ids to be downloaded
        :param version: whether the result should be an object or a string
        :return: a result list
        """

        connections = len(missing_order_id_list)
        result = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=connections) as executor:

            future_to_url = (executor.submit(self._download_order_by_id, order_id, version) for order_id in missing_order_id_list)

            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    data = future.result()
                    result.append(data)
                except Exception as e:
                    raise e

                if self._shut_down:
                    executor.shutdown(wait=False, cancel_futures=True)

        return result

    def _download_order_by_id(self, order_id, version):
        """
        A method to download one order by id
        :param order_id: the id of the order to be downloaded
        :param version: what kind of information to be downloaded
        :return: the result
        """

        if version == "json":
            result = self._GodsUnchainedPoller._get_json_by_order_id(order_id)

        elif version == "order":
            result = self._GodsUnchainedPoller.get_order_by_order_id(order_id)

        return result, order_id
