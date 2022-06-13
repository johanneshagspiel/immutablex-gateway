from scrappers.gods_unchained_poller import Gods_Unchained_Poller
import concurrent.futures


class Parallel_Order_By_Sell_Token_ID_Downloader():

    def __init__(self):
        self._gp = Gods_Unchained_Poller()

    def parallel_download_orders_by_sell_token_id(self, token_id_list):

        connections = len(token_id_list)
        result = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=connections) as executor:

            order_futures = (executor.submit(self._download_orders_by_token_id, token_id) for token_id in token_id_list)

            for future in concurrent.futures.as_completed(order_futures):
                try:
                    data = future.result()
                    result.append(data)
                except Exception as e:
                    raise

        return result


    def _download_orders_by_token_id(self, token_id):

        result = self._gp._get_jsons_by_sell_token_id(token_id)

        return result
