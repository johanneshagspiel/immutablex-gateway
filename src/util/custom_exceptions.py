import pytz

from util.files.file_io_helper import File_IO_Helper
from util.url.url_analzyer import URL_Analyzer
from datetime import datetime

class Card_Sale_Interruption(Exception):

    def __init__(self, message =""):
        self.message = message
        super().__init__(self.message)


class TooManyAPICalls(Exception):

    def __init__(self, url=None, write_to_file=False, message="Too many API calls have been made"):

        self.message = message
        super().__init__(self.message)

        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc)
        current_time_str = datetime.strftime(current_time_utc, "%Y-%m-%dT%H:%M:%S.%fZ")

        if write_to_file:

            if url != None:
                info_str, info_dic = URL_Analyzer.analyze_url(url)

                write_to_file_dic = {}
                write_to_file_dic["status"] = info_dic["status"]
                write_to_file_dic["type"] = info_dic["type"]
                write_to_file_dic["from"] = info_dic["from"]
                write_to_file_dic["to"] = info_dic["to"]
                write_to_file_dic["error_type"] = "<class 'Custom_Exceptions.TooManyAPICalls'>"
                write_to_file_dic["timestamp"] = current_time_str

                File_IO_Helper.write_too_many_api_calls(write_to_file_dic)

class Internal_Server_Error(Exception):

    def __init__(self, url=None, write_to_file=False, message="There was an internal server error at Immutable X"):

        self.message = message
        super().__init__(self.message)

        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc)
        current_time_str = datetime.strftime(current_time_utc, "%Y-%m-%dT%H:%M:%S.%fZ")

        if url != None:
            info_str, info_dic = URL_Analyzer.analyze_url(url)

        if write_to_file:
            write_to_file_dic = {}
            write_to_file_dic["status"] = info_dic["status"]
            write_to_file_dic["type"] = info_dic["type"]
            write_to_file_dic["from"] = info_dic["from"]
            write_to_file_dic["to"] = info_dic["to"]
            write_to_file_dic["error_type"] = "<class 'Custom_Exceptions.Internal_Server_Error'>"
            write_to_file_dic["timestamp"] = current_time_str

            File_IO_Helper.write_internal_server_error(write_to_file_dic)


class Download_Log_Error(Exception):

    def __init__(self, combination):
        combination_string = ", ".join(combination)
        self.message = f"The last download was not finished properly - please check the last files for {combination_string} and then reset the download_log file"
        super().__init__(self.message)


class Response_Error(Exception):

    def __init__(self, response, error_type, url, write_to_file):
        self.response_text = str(response.text)
        self.status_code = str(response.status_code)
        self.error_type = str(error_type)

        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc)
        current_time_str = datetime.strftime(current_time_utc, "%Y-%m-%dT%H:%M:%S.%fZ")

        if write_to_file:
            info_str, info_dic = URL_Analyzer.analyze_url(url)
            self.message = f"Something went wrong with the response to the request {info_str} as the {self.error_type} exception occurred"

            write_to_file_dic = {}
            write_to_file_dic["status"] = info_dic["status"]
            write_to_file_dic["type"] = info_dic["type"]
            write_to_file_dic["from"] = info_dic["from"]
            write_to_file_dic["to"] = info_dic["to"]
            write_to_file_dic["error_type"] = self.error_type
            write_to_file_dic["timestamp"] = current_time_str
            write_to_file_dic["status_code"] = self.status_code

            File_IO_Helper.write_response_error(write_to_file_dic)

        else:
            self.message = f"Something went wrong with the response to the request as the {self.error_type} exception occurred"

        super().__init__(self.message)


class Request_Error(Exception):

    def __init__(self, error_type, url, write_to_file):
        self.error_type = str(error_type)

        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc)
        current_time_str = datetime.strftime(current_time_utc, "%Y-%m-%dT%H:%M:%S.%fZ")

        if write_to_file:
            info_str, info_dic = URL_Analyzer.analyze_url(url)
            self.message = f"Something went wrong when requesting {info_str} as the {self.error_type} exception occurred"

            write_to_file_dic = {}
            write_to_file_dic["status"] = info_dic["status"]
            write_to_file_dic["type"] = info_dic["type"]
            write_to_file_dic["from"] = info_dic["from"]
            write_to_file_dic["to"] = info_dic["to"]
            write_to_file_dic["error_type"] = self.error_type
            write_to_file_dic["timestamp"] = current_time_str

            File_IO_Helper.write_request_error(write_to_file_dic)

        else:
            self.message = f"Something went wrong with this request as the {self.error_type} exception occurred"

        super().__init__(self.message)


class Start_New_Day_Error(Exception):

    def __init__(self):
        self.message = "We are close to the start of a new day in the UTC time zone - time to download the latest currency prices"
        super().__init__(self.message)
