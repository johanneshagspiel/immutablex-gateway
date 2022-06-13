from scrappers.gods_unchained_poller import Gods_Unchained_Poller
import concurrent.futures


class Parallel_Orders_In_Section_Downloader:

    def __init__(self):
        self._gp = Gods_Unchained_Poller()
        self._shut_down = False

    def parallel_download_orders_in_sections(self, get_type_str, section_to_download_list):

        connections = len(section_to_download_list)
        result = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=connections) as executor:

            future_to_section = (executor.submit(self._load_section, get_type_str, section_to_download_dic) for section_to_download_dic in section_to_download_list)

            for future in concurrent.futures.as_completed(future_to_section):
                try:
                    data = future.result()
                    result.append(data)
                except Exception as e:
                    raise

                if self._shut_down:
                    executor.shutdown(wait=False, cancel_futures=True)

        return result


    def _load_section(self, get_type_str, section_to_download_dic):
        from_timestamp_str = section_to_download_dic["from"]
        to_timetstamp_str = section_to_download_dic["to"]

        result = self._gp.get_orders_based_on_timestamp(get_type_str=get_type_str, status_str=None, from_time_stamp_str=from_timestamp_str, to_time_stamp_str=to_timetstamp_str)

        return (result, section_to_download_dic)
