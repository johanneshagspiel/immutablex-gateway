from src.scrappers.godsunchainedpoller import GodsUnchainedPoller
import concurrent.futures


class ParallelOrderBySellTokenIDDownloader:
    """
    A class to parallel download orders by the sell token id
    """

    def __init__(self):
        """
        The constructor of the ParallelOrderBySellTokenIDDownloader class
        """
        self._gp = GodsUnchainedPoller()

    def parallel_download_orders_by_sell_token_id(self, token_id_list):
        """
        A method to parallel download orders by sell token id
        :param token_id_list: the sell token id list
        :return: the result
        """

        connections = len(token_id_list)
        result = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=connections) as executor:

            order_futures = (executor.submit(self._download_orders_by_token_id, token_id) for token_id in token_id_list)

            for future in concurrent.futures.as_completed(order_futures):
                try:
                    data = future.result()
                    result.append(data)
                except Exception:
                    raise

        return result

    def _download_orders_by_token_id(self, token_id):
        """
        A method to download one order by token id
        :param token_id: the token id of the card to be downloaded
        :return: result
        """

        result = self._gp._get_jsons_by_sell_token_id(token_id)

        return result
