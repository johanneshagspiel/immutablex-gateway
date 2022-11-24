from src.operators.client import Client
from src.operators.helpers.file_helpers import FileHandler
from src.util.files.fileiohelper import FileIoHelper


class CurrencyHelper:
    """
    A class to deal with the changing currencies on immutable x
    """

    def __init__(self):
        """
        The constructor of the CurrencyHelper class
        """
        pass

    def check_for_new_currencies(self):
        """
        A method to check whether new currencies are supported by immutable x
        :return: Boolean, ErrorString
        """

        client = Client()
        token_list = client.get_list_of_all_tokens_that_exist()
        currency_overview_list = [(x["token_address"], x["symbol"]) for x in token_list]

        currency_overview_file_path = FileHandler.get_base_path("currency_overview_file")

        previous_currency_overview_list = FileIoHelper.read_currency_overview_to_file(currency_overview_file_path)

        previous_currency_overview_set = set()
        for token_address, symbol in previous_currency_overview_list:
            previous_currency_overview_set.add((token_address, symbol))

        current_currency_overview_set = set()
        for token_address, symbol in currency_overview_list:
            current_currency_overview_set.add((token_address, symbol))

        not_implemented = current_currency_overview_set - previous_currency_overview_set
        gotten_rid_of = previous_currency_overview_set - current_currency_overview_set

        if len(not_implemented) > 0:

            exception_string = ""

            for token_address, symbol in not_implemented:
                exception_string += f"Token \"{symbol}\" with address \"{token_address}\" has not been implemented\n"

            for token_address, symbol in gotten_rid_of:
                exception_string += f"Token \"{symbol}\" with address \"{token_address}\" no longer is supported\n"

            return False, exception_string
        else:
            return True, None

    def write_current_token_overview_to_file(self):
        """
        A method to write the new supported currencies to file
        :return: None
        """
        client = Client()
        token_list = client.get_list_of_all_tokens_that_exist()
        currency_overview_list = [(x["token_address"], x["symbol"]) for x in token_list]

        currency_overview_file_path = FileHandler.get_base_path("currency_overview_file")
        FileIoHelper.write_currency_overview_to_file(currency_overview_list, currency_overview_file_path)
