import concurrent
from datetime import datetime
from requests.exceptions import ProxyError, SSLError, ChunkedEncodingError
import requests


class RequestScheduler:
    """
    A class to schedule requests
    """

    def __init__(self, type, number_concurrent_requests, timeout_duration):
        """
        The constructor of the RequestScheduler
        :param type: the type of the order
        :param number_concurrent_requests: how many concurrent requests can be made
        :param timeout_duration: how long the to wait until a request times out
        """
        self.type = type
        self.number_concurrent_requests = number_concurrent_requests

        self.action_list = []
        self.sender_dic = {}

        self.keep_going = True
        self.timeout_duration = timeout_duration

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1000)

    def add_action(self, action, additional_info, sender):
        """
        A method to add one action to execute
        :param action: the action to be executed
        :param additional_info: additional information associated with the action
        :param sender: the sender of the action
        :return: None
        """
        self.sender_dic[sender] = None
        self.action_list.append((action, additional_info, sender))

    def obtain_future(self, sender):
        """
        A method to obtain the future associated with a sender
        :param sender: the sender
        :return: the future associated with the sender
        """
        entry = self.sender_dic[sender]

        if entry:
            self.sender_dic.pop('key', None)

        return entry

    def run(self):
        """
        A method to run one action
        :return: None
        """

        while self.keep_going:

            start_time = datetime.utcnow()

            if len(self.action_list) > self.number_concurrent_requests:
                number_of_submissions = self.number_concurrent_requests
            else:
                number_of_submissions = len(self.action_list)

            for submission in range(number_of_submissions):
                action, additional_info, sender = self.action_list.pop()
                future = self.executor.submit(self.execute_request, action, additional_info)
                self.sender_dic[sender] = future

            print(len(self.action_list))

            wait_before_go_on = True
            while wait_before_go_on:
                end_time = datetime.utcnow()
                time_difference_seconds = (end_time - start_time).total_seconds()
                if time_difference_seconds > 1:
                    wait_before_go_on = False


    def execute_request(self, action, additional_info):
        """
        A method to execute one request
        :param action: the kind of request to be made
        :param additional_info: the additional information associated with the action
        :return: None
        """

        if action == "get_request":

            headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36", "Accept-Language" : "en-US", "Accept": "application/json"}

            if self.type == "proxy":

                http_proxy = ""
                https_proxy = ""
                proxy_dic = {
                    "http": http_proxy,
                    "https": https_proxy,
                }

                download_not_finished = True
                while download_not_finished:
                    try:
                        response = requests.request("GET", additional_info, headers=headers, timeout=self.timeout_duration, proxies=proxy_dic)
                        download_not_finished = False
                    except (ProxyError, SSLError, ChunkedEncodingError) as proxy_error:
                        None

            elif self.type == "normal":

                response = requests.request("GET", additional_info, headers=headers, timeout=self.timeout_duration)
