import json
import random
import time
import traceback
from datetime import datetime
import requests
from ratelimiter import RateLimiter

from src.util.custom_exceptions import RequestError, TooManyAPICalls, ResponseError, InternalServerError
from src.util.url.urlcreator import UrlCreator


class ImmutableXScrapper:
    """
    A class to make requests to the IMX api
    """

    def __init__(self):
        """
        The constructor of the ImmutableXScrapper class
        """
        self.request_scheduler = None
        self.waiting = True

    def set_request_scheduler(self, request_scheduler):
        self.request_scheduler = request_scheduler


    def make_get_request(self, url, checking_for_internal_errors=True, add_download_time_info=False, write_errors=False, timeout_duration=None):
        """
        A method to make get requests
        :param url: the url to make the get request to
        :param checking_for_internal_errors: whether to check the result for internal errors
        :param add_download_time_info: whether to add download information to the result
        :param write_errors: whether to write down errors
        :param timeout_duration: the duration of the timeout
        :return: the result
        """

        return self.download_get_request(url, checking_for_internal_errors, add_download_time_info, write_errors, timeout_duration)


    @RateLimiter(max_calls=10, period=1)
    def make_one_request(self, url, headers, timeout_duration):

        return requests.request("GET", url, headers=headers, timeout=timeout_duration)

    def download_get_request(self, url, checking_for_internal_errors=True, add_download_time_info=False, write_errors=False, timeout_duration=None):

        headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36", "Accept-Language" : "en-US", "Accept": "application/json"}

        result_list = []

        try:
            #response = requests.request("GET", url, headers=headers, timeout=timeout_duration)
            response = self.make_one_request(url=url, headers=headers, timeout_duration=timeout_duration)
        except Exception as e:
            traceback.print_exc()
            raise RequestError(type(e), url, write_errors)

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

                        next_url = UrlCreator.create_next_cursor_url(url, next_cursor_url)

                        try:
                            #next_response = requests.request("GET", next_url, headers=headers, timeout=timeout_duration)
                            next_response = self.make_one_request(url=next_url, headers=headers, timeout_duration=timeout_duration)
                        except Exception as e:
                            traceback.print_exc()
                            raise RequestError(type(e), next_url, write_errors)

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
                                raise ResponseError(response, type(e), url, write_errors)

            else:
                if add_download_time_info:
                    result_list.append((datetime.utcnow().isoformat().replace("+00:00", "Z"), parsed))
                else:
                    result_list.append(parsed)

        except (ResponseError, RequestError, TooManyAPICalls) as custom_errors:
            raise custom_errors

        except Exception as e:
            if response.status_code == 429:
                raise TooManyAPICalls(url, write_errors)
            else:
                raise ResponseError(response, type(e), url, write_errors)

        if checking_for_internal_errors:
            self._check_for_internal_server_error(results=result_list, add_download_time_info=add_download_time_info, url=url, write_errors=write_errors)

        return result_list

    def _check_for_internal_server_error(self, results, add_download_time_info, url, write_errors):
        """
        A method to check the results for internal error
        :param results: the results to check
        :param add_download_time_info: whether time information is stored
        :param url: the url of the request
        :param write_errors: whether to write down errors
        :return: None
        """

        if add_download_time_info:
            for download_timestamp, order_json_list in results:
                for order_json in order_json_list:
                    if "code" in order_json:
                        raise InternalServerError(url, write_errors)

        else:
            for order_json in results:
                if "code" in order_json:
                    raise InternalServerError(url, write_errors)
