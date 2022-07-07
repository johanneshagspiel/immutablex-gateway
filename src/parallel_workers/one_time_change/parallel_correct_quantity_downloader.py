import concurrent.futures
import json
import datetime
import logging
#logging.basicConfig(level=logging.DEBUG)
from scrappers.coinapi_scrapper import CoinAPI_Scrapper
from scrappers.godsunchainedpoller import GodsUnchainedPoller
from util.custom_exceptions import TooManyAPICalls, Response_Error
from util.number_converter import Number_Converter


class Parallel_Correct_Quantity_Downloader():

    def __init__(self):
        self._GodsUnchainedPoller = GodsUnchainedPoller()
        self._logger = logging.getLogger(__name__)
        self._historical_prices_dic = CoinAPI_Scrapper.get_historical_prices()

    def parallel_download_correct_quantity(self, to_correct_df):
        amount_connections = len(to_correct_df)
        result_list = []
        encountered_error = False

        with concurrent.futures.ThreadPoolExecutor(max_workers=amount_connections) as executor:

            updated_rows = (executor.submit(self._download_correct_quantity, row) for index, row in to_correct_df.iterrows())

            for updated_row in concurrent.futures.as_completed(updated_rows):

                try:
                    encountered_error_temp, row = updated_row.result()

                    if encountered_error_temp == True:
                        encountered_error = True

                except Exception as exc:
                    encountered_error = True

                finally:
                    result_list.append(row)

        return (result_list, encountered_error)

    def _download_correct_quantity(self, row):

        encountered_error = False

        try:
            order = self._GodsUnchainedPoller.get_order_by_order_id(int(row["order_id"]))
            correct_quantity = order["buy"]["data"]["quantity"]
            correct_decimals = order["buy"]["data"]["decimals"]

            updated_timestamp = row["updated_timestamp"]
            updated_timestamp_day = datetime.datetime.strftime(updated_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").split('T')[0]

            currency = row["currency"]

            price_crypto_as_float = Number_Converter.get_float_from_quantity_decimal(correct_quantity, correct_decimals)
            historical_price = self._historical_prices_dic[updated_timestamp_day][currency]

            if historical_price != None:
                new_price_euro = historical_price * price_crypto_as_float
            else:
                new_price_euro = None

            row["quantity"] = correct_quantity
            row["decimals"] = correct_decimals
            row["price_euro_at_ut_day"] = new_price_euro

        except Exception as e:
            encountered_error = True

        return encountered_error, row
