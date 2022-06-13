import concurrent.futures
from scrappers.gods_unchained_poller import Gods_Unchained_Poller


class Parallel_Order_ID_Downloader():

    def __init__(self):
        self._gods_unchained_poller = Gods_Unchained_Poller()
        self._shut_down = False

    def parallel_download_orders_by_id(self, missing_order_id_list, version):

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

        if version == "json":
            result = self._gods_unchained_poller._get_json_by_order_id(order_id)

        elif version == "order":
            result = self._gods_unchained_poller.get_order_by_order_id(order_id)

        return (result, order_id)
