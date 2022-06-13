import json
from datetime import datetime
import requests
from requests.exceptions import ProxyError, SSLError, ChunkedEncodingError

from util.custom_exceptions import Request_Error, TooManyAPICalls, Response_Error, Internal_Server_Error
from util.url.url_creator import URL_Creator


class Immutable_X_Scrapper:

    def __init__(self):
        None

    def make_get_request(self, url, checking_for_internal_errors=True, add_download_time_info=False, write_errors=False, timeout_duration=None):

        headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36", "Accept-Language" : "en-US", "Accept": "application/json"}

        http_proxy = "http://mrjojo11:Qp2IqLRlG6vn9W2A@proxy.packetstream.io:31112"
        https_proxy = "http://mrjojo11:Qp2IqLRlG6vn9W2A@proxy.packetstream.io:31112"
        proxy_dic = {
            "http": http_proxy,
            "https": https_proxy,
        }

        result_list = []

        try:
            response = requests.request("GET", url, headers=headers, timeout=timeout_duration)
        except Exception as e:
            raise Request_Error(type(e), url, write_errors)

        # download_not_finished = True
        # while download_not_finished:
        #     try:
        #         response = requests.request("GET", url, headers=headers, timeout=timeout_duration, proxies=proxy_dic)
        #         download_not_finished = False
        #     except (ProxyError, SSLError, ChunkedEncodingError) as proxy_error:
        #         None
        #     except Exception as e:
        #         print(type(e))
        #         raise Request_Error(type(e), url, write_errors)

        try:
            parsed = json.loads(response.text)

            if "result" in parsed:

                results = parsed['result']

                if add_download_time_info:
                    result_list.append((datetime.utcnow().isoformat().replace("+00:00", "Z"), results))
                else:
                    result_list.extend(results)

                next_cursor_url = parsed['cursor']

                if parsed['remaining'] != 0:
                    check_next = True

                    while check_next:

                        next_url = URL_Creator.create_next_cursor_url(url, next_cursor_url)

                        try:
                            next_response = requests.request("GET", next_url, headers=headers, timeout=timeout_duration)
                        except Exception as e:
                            raise Request_Error(type(e), url, write_errors)

                        # download_not_finished = True
                        # while download_not_finished:
                        #     try:
                        #         next_response = requests.request("GET", next_url, headers=headers, timeout=timeout_duration, proxies=proxy_dic)
                        #         download_not_finished = False
                        #     except (ProxyError, SSLError, ChunkedEncodingError) as proxy_error:
                        #         None
                        #     except Exception as e:
                        #         print(type(e))
                        #         raise Request_Error(type(e), url, write_errors)

                        try:
                            parsed = json.loads(next_response.text)

                            if "result" in parsed:
                                next_results = parsed['result']

                                if add_download_time_info:
                                    result_list.append((datetime.utcnow().isoformat().replace("+00:00", "Z"), next_results))
                                else:
                                    result_list.extend(next_results)

                                if parsed['remaining'] != 1:
                                    check_next = False
                                else:
                                    next_cursor_url = parsed['cursor']

                            else:
                                if add_download_time_info:
                                    result_list.append((datetime.utcnow().isoformat().replace("+00:00", "Z"), parsed))
                                else:
                                    result_list.append(parsed)

                        except Exception as e:
                            if response.status_code == 429:
                                raise TooManyAPICalls(url, write_errors)
                            else:
                                raise Response_Error(response, type(e), url, write_errors)

            else:
                if add_download_time_info:
                    result_list.append((datetime.utcnow().isoformat().replace("+00:00", "Z"), parsed))
                else:
                    result_list.append(parsed)


        except (Response_Error, Request_Error, TooManyAPICalls) as custom_errors:
            raise custom_errors

        except Exception as e:
            if response.status_code == 429:
                raise TooManyAPICalls(url, write_errors)
            else:
                raise Response_Error(response, type(e), url, write_errors)

        if checking_for_internal_errors:
            self._check_for_internal_server_error(results=result_list, add_download_time_info=add_download_time_info, url=url, write_errors=write_errors)

        return result_list


    ### Check for Internal Server Errors ##############################################################################

    def _check_for_internal_server_error(self, results, add_download_time_info, url, write_errors):

        if add_download_time_info:
            for download_timestamp, order_json_list in results:
                for order_json in order_json_list:
                    if "code" in order_json:
                        raise Internal_Server_Error(url, write_errors)

        else:
            for order_json in results:
                if "code" in order_json:
                    raise Internal_Server_Error(url, write_errors)
