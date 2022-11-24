import json
import datetime
import pytz
import requests
from requests import Session, Timeout, TooManyRedirects
from src.util.files.filehandler import FileHandler


class CoinMarketCapScrapper:
    """
    A class to interact with coinmarketcap.com to download the current cryptocurrency prices
    """

    coinmarketcap_info_file_path = FileHandler.get_base_path("coinmarketcap_info_file")
    with open(coinmarketcap_info_file_path, 'r', encoding='utf-8') as coinmarketcap_info_file:
        coinmarketcap_info_dic = json.load(coinmarketcap_info_file)
    coinmarketcap_info_file.close()

    temp_api_key = coinmarketcap_info_dic["api_key"]
    if len(temp_api_key) == 0:
        raise Exception("No key for CoinMarketCap found - information_dic one here https://coinmarketcap.com/api/ and add it to resources/client_info/coinmarketcap_info.json")
    else:
        _api_key = temp_api_key

    def __init__(self):
        """
        The constructor of the CoinMarketCapScrapper class
        """
        pass

    @staticmethod
    def _download_latest_currency_prices():
        """
        A method to download the latest cryptocurrency prices
        :return: None
        """

        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        parameters = {
            'symbol': "ETH,GODS,IMX,USDC,GOG,OMI,APE,CMT,VCO,VCORE",
            'convert': 'EUR'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': CoinMarketCapScrapper._api_key,
        }

        session = Session()
        session.headers.update(headers)

        information_not_downloaded = True
        while information_not_downloaded:
            try:
                response = session.get(url, params=parameters)
                session.close()
                information_not_downloaded = False
            except (requests.exceptions.ConnectionError, Timeout, TooManyRedirects, requests.exceptions.ChunkedEncodingError) as e:
                print(f"Coin_Market_Cap experienced {e}")

        data = json.loads(response.text)
        result = data["data"]

        cleaned_dic = {}
        for key,value in result.items():
            cleaned_dic[key] = value["quote"]["EUR"]["price"]

        final_dic = {}
        final_dic["prices"] = cleaned_dic

        currencies = ["ETH", "GODS", "IMX", "USDC", "GOG", "OMI", "APE", "CMT", "VCO", "VCORE"]

        for currency in currencies:
            if currency not in final_dic["prices"]:
                final_dic["prices"][currency] = 0

        current_time = datetime.datetime.now()
        utc_time = current_time.astimezone(pytz.utc).isoformat().replace("+00:00", "Z")
        final_dic["time_stamp"] = utc_time

        with open(FileHandler.get_base_path("current_currency_prices"), 'w', encoding='utf-8') as currency_prices_file:
            json.dump(final_dic, currency_prices_file, ensure_ascii=False, indent=4)
        currency_prices_file.close()

    @staticmethod
    def _read_currency_prices_file():
        """
        A method to read the current currency price file
        :return: the current cryptocurrency dictionary, the last timestamp downloaded
        """
        with open(FileHandler.get_base_path("current_currency_prices"), 'r', encoding='utf-8') as currency_prices_file:
            temp_currency_price_file = json.load(currency_prices_file)
        currency_prices_file.close()

        if "prices" in temp_currency_price_file:
            currency_prices_dic = temp_currency_price_file["prices"]
            last_time_stamp = temp_currency_price_file["time_stamp"]
        else:
            currency_prices_dic = {}
            last_time_stamp = "2021-06-01T00:00:00.000000Z"

        return currency_prices_dic, last_time_stamp

    @staticmethod
    def get_latest_currency_price():
        """
        A method to get the latest currency prices either by downloading them or reading them from file
        :return: the current cryptocurrency price dictionary
        """
        currency_prices_dic, last_time_stamp = CoinMarketCapScrapper._read_currency_prices_file()

        time_in_file = datetime.datetime.strptime(last_time_stamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        current_time = datetime.datetime.now()
        utc_time = current_time.astimezone(pytz.utc).replace(tzinfo=None)

        difference = utc_time - time_in_file

        if difference.total_seconds() > 300:
            CoinMarketCapScrapper._download_latest_currency_prices()
            return CoinMarketCapScrapper._read_currency_prices_file()[0]
        else:
            return currency_prices_dic

    @staticmethod
    def get_now_currency_price():
        """
        A method to get the cryptocurrency prices at this moment
        :return: the latest cryptocurrency price dictionary
        """
        CoinMarketCapScrapper._download_latest_currency_prices()
        return CoinMarketCapScrapper._read_currency_prices_file()[0]
