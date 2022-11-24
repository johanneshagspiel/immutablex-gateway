import concurrent
import functools
from datetime import datetime
from requests.exceptions import ProxyError, SSLError, ChunkedEncodingError
import requests

from src.util.helpers import TaskToConsolePrinter


class RequestScheduler:
    """
    A class to schedule requests
    """

    def __init__(self, number_concurrent_requests=5):
        """
        The constructor of the RequestScheduler
        :param type: the type of the order
        :param number_concurrent_requests: how many concurrent requests can be made
        :param timeout_duration: how long the to wait until a request times out
        """
        self.number_concurrent_requests = number_concurrent_requests

        self.action_list = []
        self.sender_dic = {}
        self.result_dic = {}

        self.keep_going = True

    def add_action(self, action, additional_info, sender, identifier):
        """
        A method to add one action to execute
        :param action: the action to be executed
        :param additional_info: additional information associated with the action
        :param sender: the sender of the action
        :return: None
        """
        # self.result_dic[identifier] = None
        # self.sender_dic[identifier] = None
        self.action_list.append((action, additional_info, sender, identifier))

    def obtain_future(self, identifier):
        """
        A method to obtain the future associated with a sender
        :param sender: the sender
        :return: the future associated with the sender
        """

        if identifier in self.result_dic:

            entry = self.result_dic[identifier]

            if entry:
                self.result_dic.pop(identifier, None)

            if isinstance(entry, concurrent.futures._base.Future):
                entry = entry.result()

            return entry

        else:
            return False

    def inform_sender(self, sender):
        sender.waiting = False

    def run(self):
        """
        A method to run one action
        :return: None
        """
        #self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

        while self.keep_going:

            with concurrent.futures.ThreadPoolExecutor(20) as executor:

                start_time = datetime.utcnow()

                if len(self.action_list) > self.number_concurrent_requests:
                    number_of_submissions = self.number_concurrent_requests
                else:
                    number_of_submissions = len(self.action_list)

                action_list = []
                additional_info_list = []
                sender_list = []
                identifier_list = []

                for submission in range(number_of_submissions):
                    action, additional_info, sender, identifier = self.action_list.pop()
                    action_list.append(action)
                    additional_info_list.append(additional_info)
                    sender_list.append(sender)
                    identifier_list.append(identifier)

                executor.map(self.execute_request, action_list, additional_info_list, sender_list, identifier_list)
                    # future = self.executor.submit(self.execute_request, action, additional_info)
                    # future.add_done_callback(functools.partial(inform_sender, self, sender, identifier))

                wait_before_go_on = True
                while wait_before_go_on:
                    end_time = datetime.utcnow()
                    time_difference_seconds = (end_time - start_time).total_seconds()
                    if time_difference_seconds > 1:
                        wait_before_go_on = False


    def execute_request(self, action, additional_info, sender, identifier):
        """
        A method to execute one request
        :param action: the kind of request to be made
        :param additional_info: any additional information needed
        :return: None
        """
        print("test")

        if action == "GET":

            headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36", "Accept-Language" : "en-US", "Accept": "application/json"}

            # TaskToConsolePrinter.print_downloading_task_info(status_string=status_string,
            #                                                  get_type_string=get_type_string,
            #                                                  from_str=start_time_stamp_str,
            #                                                  to_str=time_stamp_str_list[-1][1])
            #print(str(datetime.now()))


            result = requests.request("GET", url=additional_info, headers=headers)

            self.result_dic[identifier] = datetime.utcnow().isoformat().replace("+00:00", "Z"), result
            self.inform_sender(sender)
