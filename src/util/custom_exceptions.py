import pytz
from src.util.files.fileiohelper import FileIoHelper
from src.util.url.url_analzyer import UrlAnalyzer
from datetime import datetime


class CardSaleInterruption(Exception):
    """
    An exception raised during the card sale process
    """

    def __init__(self, message =""):
        """
        The constructor for the CardSaleInterruption exception
        :param message: the message to be shown
        """
        self.message = message
        super().__init__(self.message)


class TooManyAPICalls(Exception):
    """
    An excpetion raised when too many api calls have been made
    """

    def __init__(self, url=None, write_to_file=False, message="Too many API calls have been made"):
        """
        The constructor of the TooManyAPICalls exception
        :param url: the urls of the request
        :param write_to_file: whether to write this exception to file
        :param message: the message to be shown
        """

        self.message = message
        super().__init__(self.message)

        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc)
        current_time_str = datetime.strftime(current_time_utc, "%Y-%m-%dT%H:%M:%S.%fZ")

        if write_to_file:

            if url != None:
                info_str, info_dic = UrlAnalyzer.analyze_url(url)

                write_to_file_dic = {}
                write_to_file_dic["status"] = info_dic["status"]
                write_to_file_dic["type"] = info_dic["type"]
                write_to_file_dic["from"] = info_dic["from"]
                write_to_file_dic["to"] = info_dic["to"]
                write_to_file_dic["error_type"] = "<class 'Custom_Exceptions.TooManyAPICalls'>"
                write_to_file_dic["timestamp"] = current_time_str

                FileIoHelper.write_too_many_api_calls(write_to_file_dic)


class InternalServerError(Exception):
    """
    An exception raised when the results indicate that an internal server error has occurred
    """

    def __init__(self, url=None, write_to_file=False, message="There was an internal server error at Immutable X"):
        """
        The constructor of the InternalServerError exception
        :param url: the urls of the request
        :param write_to_file: whether to write this error to file
        :param message: the message to be shown
        """

        self.message = message
        super().__init__(self.message)

        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc)
        current_time_str = datetime.strftime(current_time_utc, "%Y-%m-%dT%H:%M:%S.%fZ")

        if url != None:
            info_str, info_dic = UrlAnalyzer.analyze_url(url)

        if write_to_file:
            write_to_file_dic = {}
            write_to_file_dic["status"] = info_dic["status"]
            write_to_file_dic["type"] = info_dic["type"]
            write_to_file_dic["from"] = info_dic["from"]
            write_to_file_dic["to"] = info_dic["to"]
            write_to_file_dic["error_type"] = "<class 'Custom_Exceptions.Internal_Server_Error'>"
            write_to_file_dic["timestamp"] = current_time_str

            FileIoHelper.write_internal_server_error(write_to_file_dic)


class DownloadLogError(Exception):
    """
    An exception raised when the last download has not finished correctly
    """

    def __init__(self, combination):
        """
        The constructor of the DownloadLogError exception
        :param combination: the errors encountered
        """
        combination_string = ", ".join(combination)
        self.message = f"The last download was not finished properly - please check the last files for {combination_string} and then reset the download_log file"
        super().__init__(self.message)


class ResponseError(Exception):
    """
    An exception to be raised when the response to a request is faulty
    """

    def __init__(self, response, error_type, url, write_to_file):
        """
        The constructor of the ResponseError exception
        :param response: the faulty response
        :param error_type: what kind of error encountered
        :param url: the url of the request
        :param write_to_file: whether to write the exception to file
        """
        self.response_text = str(response.text)
        self.status_code = str(response.status_code)
        self.error_type = str(error_type)

        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc)
        current_time_str = datetime.strftime(current_time_utc, "%Y-%m-%dT%H:%M:%S.%fZ")

        if write_to_file:
            info_str, info_dic = UrlAnalyzer.analyze_url(url)
            self.message = f"Something went wrong with the response to the request {info_str} as the {self.error_type} exception occurred"

            write_to_file_dic = {}
            write_to_file_dic["status"] = info_dic["status"]
            write_to_file_dic["type"] = info_dic["type"]
            write_to_file_dic["from"] = info_dic["from"]
            write_to_file_dic["to"] = info_dic["to"]
            write_to_file_dic["error_type"] = self.error_type
            write_to_file_dic["timestamp"] = current_time_str
            write_to_file_dic["status_code"] = self.status_code

            FileIoHelper.write_response_error(write_to_file_dic)

        else:
            self.message = f"Something went wrong with the response to the request as the {self.error_type} exception occurred"

        super().__init__(self.message)


class RequestError(Exception):
    """
    An exception raised when something went wrong with the request
    """

    def __init__(self, error_type, url, write_to_file):
        """
        The constructor of the RequestError exception
        :param error_type: the type of error encountered
        :param url: the url of the request
        :param write_to_file: whether to write the error to file
        """
        self.error_type = str(error_type)

        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc)
        current_time_str = datetime.strftime(current_time_utc, "%Y-%m-%dT%H:%M:%S.%fZ")

        if write_to_file:
            info_str, info_dic = UrlAnalyzer.analyze_url(url)
            self.message = f"Something went wrong when requesting {info_str} as the {self.error_type} exception occurred"

            write_to_file_dic = {}
            write_to_file_dic["status"] = info_dic["status"]
            write_to_file_dic["type"] = info_dic["type"]
            write_to_file_dic["from"] = info_dic["from"]
            write_to_file_dic["to"] = info_dic["to"]
            write_to_file_dic["error_type"] = self.error_type
            write_to_file_dic["timestamp"] = current_time_str

            FileIoHelper.write_request_error(write_to_file_dic)

        else:
            self.message = f"Something went wrong with this request as the {self.error_type} exception occurred"

        super().__init__(self.message)


class StartNewDayError(Exception):
    """
    An exception to be raised when a new day has started
    """

    def __init__(self):
        """
        The constructor of the StartNewDayError exception
        """
        self.message = "We are close to the start of a new day in the UTC time zone - time to download the latest currency prices"
        super().__init__(self.message)
