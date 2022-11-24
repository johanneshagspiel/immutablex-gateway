import json
import time
from datetime import datetime
import pytz
import requests
from src.util.files.filehandler import FileHandler
from src.util.files.fileiohelper import FileIoHelper


class CoinAPIScrapper:
    """
    A class to interact with coinapi.io to get historical crypto currency prices
    """

    coinapi_info_file_path = FileHandler.get_base_path("coinapi_info_file")
    with open(coinapi_info_file_path, 'r', encoding='utf-8') as coinapi_info_file:
        coinapi_info_dic = json.load(coinapi_info_file)
    coinapi_info_file.close()

    temp_api_key = coinapi_info_dic["api_key"]
    if len(temp_api_key) == 0:
        raise Exception("No key for CoinAPI found - information_dic one here https://www.coinapi.io/pricing/ and add it to resources/client_info/coinapi_info.json")
    else:
        _api_key = temp_api_key

    _base_url = "https://rest.coinapi.io/v1/"

    def __init__(self):
        """
        The constructor of the CoinAPIScrapper class
        """
        pass

    @classmethod
    def get_historical_prices(cls):
        """
        A method to get a historical prices
        :return: an overview of the historical prices as a dictionary
        """

        historical_prices_file_dic = FileIoHelper.read_historical_prices_dic()
        last_downloaded_day = CoinAPIScrapper._get_last_day_downloaded(historical_prices_file_dic)

        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc)
        current_day = f"{current_time_utc.year}-{current_time_utc.month:02d}-{current_time_utc.day:02d}"

        if current_day != last_downloaded_day:
            historical_prices_file_dic = CoinAPIScrapper._get_historical_currency_info(last_downloaded_day, current_day)

        return historical_prices_file_dic

    @staticmethod
    def _get_last_day_downloaded(historical_prices_file_dic):
        """
        A method to get the last day for which currency information was downloaded
        :param historical_prices_file_dic:
        :return:
        """

        day_list = sorted([key for key, value in historical_prices_file_dic.items()], reverse=True)

        if len(day_list) > 0:
            last_day = day_list[0]
        else:
            last_day = "2021-01-01"

        return last_day

    @classmethod
    def _get_historical_currency_info(cls, start_day, end_day):
        """
        A method to get historical currency info from a start_day to an end_day
        :param start_day: the start_day
        :param end_day: the end_day
        :return: the price overview as a dictionary
        """

        time_start = start_day + "T00:00:00.0000000Z"
        time_end = end_day + "T00:00:00.0000000Z"

        # time_start = "2022-02-02T00:00:00.0000000Z"
        # time_end = "2022-02-02T15:00:00.0000000Z"

        historical_prices_path = FileHandler.get_base_path("historical_currency_prices")

        with open(historical_prices_path, 'r', encoding='utf-8') as historical_prices_file:
            historical_prices_dic = json.load(historical_prices_file)
        historical_prices_file.close()

        currencies = ["ETH", "GODS", "IMX", "USDC", "GOG", "OMI", "APE", "CMT", "VCO", "VCORE"]

        for currency_index, currency in enumerate(currencies):

            url = cls._base_url + "exchangerate/" + str(currency) + "/EUR/history?period_id=1DAY&time_start=" + str(time_start) + "&time_end=" + str(time_end) + "&limit=100000"

            headers = {'X-CoinAPI-Key': cls._api_key}

            no_valid_result = True

            while no_valid_result:
                try:
                    response = requests.get(url, headers=headers)
                    no_valid_result = False
                except requests.exceptions.ConnectionError:
                    time.sleep(2)

            response_json = response.json()

            for entry in response_json:

                day = entry["time_period_start"].split('T')[0]
                price = entry["rate_open"]

                if day not in historical_prices_dic:
                    temp_dic = {"ETH": None, "GODS": None, "IMX": None, "USDC": None, "GOG": None, "OMI": None,
                                "APE": None, "CMT": None, "VCO": None, "VCORE": None}
                    temp_dic[currency] = price
                    historical_prices_dic[day] = temp_dic
                else:
                    prev_entry = historical_prices_dic[day]
                    prev_entry[currency] = price
                    historical_prices_dic[day] = prev_entry

        with open(historical_prices_path, 'w', encoding='utf-8') as historical_prices_file:
            json.dump(historical_prices_dic, historical_prices_file, ensure_ascii=False, indent=4)
        historical_prices_file.close()

        return historical_prices_dic

    @classmethod
    def get_price_at_point_in_past(cls, timestamp_str, currency):
        """
        :param timestamp_str: a method to get the price of a currency at a point in past
        :param currency: the cryptocurrency of interest
        :return: the price dictionary
        """

        timestamp = ':'.join(timestamp_str.split('.')[0].split(':')[:2]) + ":00.0000000Z"

        url = cls._base_url + "exchangerate/" + str(currency) + "/EUR?time=" + timestamp

        headers = {'X-CoinAPI-Key': cls._api_key}

        no_valid_result = True

        while no_valid_result:
            try:
                response = requests.get(url, headers=headers)
                no_valid_result = False
            except requests.exceptions.ConnectionError:
                time.sleep(2)

        response_json = response.json()

        return response_json["rate"]
