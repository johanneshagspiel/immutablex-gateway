from datetime import datetime, timedelta

from util.helpers import Safe_Datetime_Converter
from util.url.metadata_creator import Metadata_Creator


class URL_Creator():
    _base_url = "https://api.x.immutable.com/v1"

    def __init__(self):
        None


    @staticmethod
    def create_next_cursor_url(url, next_cursor_url):

        base_url = str(url.split("page_size=200")[0]) + "page_size=200"
        rest_url = url.split("page_size=200")[1]

        next_url = base_url + "&cursor=" + next_cursor_url + "&" + rest_url

        return next_url



    @classmethod
    def create_url_by_order_type(cls, input_status_str, token_address_dic, time_tuple, meta_data_dic):

        buy_info_str = ""
        sell_info_str = ""

        if token_address_dic:
            if "buy_address" in token_address_dic:
                buy_address = token_address_dic["buy_address"]
                split_buy_address = buy_address.split("_")

                if buy_address == "ETH":
                    buy_info_str = buy_info_str + "&buy_token_type=ETH"
                elif buy_address == "GODS":
                    buy_info_str = buy_info_str + "&buy_token_type=ERC20&buy_token_address=0xccc8cb5229b0ac8069c51fd58367fd1e622afd97"
                elif buy_address == "IMX":
                    buy_info_str = buy_info_str + "&buy_token_type=ERC20&buy_token_address=0xf57e7e7c23978c3caec3c3548e3d615c346e79ff"
                elif buy_address == "USDC":
                    buy_info_str = buy_info_str + "&buy_token_type=ERC20&buy_token_address=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
                elif buy_address == "GOG":
                    buy_info_str = buy_info_str + "&buy_token_type=ERC20&buy_token_address=0x9ab7bb7fdc60f4357ecfef43986818a2a3569c62"
                elif buy_address == "OMI":
                    buy_info_str = buy_info_str + "&buy_token_type=ERC20&buy_token_address=0xed35af169af46a02ee13b9d79eb57d6d68c1749e"
                elif (split_buy_address[0] == "NFT"):
                    buy_info_str = buy_info_str + "&buy_token_address=" + str(split_buy_address[1])
                else:
                    raise Exception(f"What else is this buy_address? {buy_address}")

            if "buy_min_quantity" in token_address_dic:
                buy_min_quantity_str = token_address_dic["buy_min_quantity"]
                buy_info_str = buy_info_str + "&buy_min_quantity=" + str(buy_min_quantity_str)


            if "sell_address" in token_address_dic:
                sell_address = token_address_dic["sell_address"]
                split_sell_address = sell_address.split("_")

                if sell_address == "ETH":
                    sell_info_str = sell_info_str + "&sell_token_type=ETH&"
                elif sell_address == "GODS":
                    sell_info_str = sell_info_str + "&sell_token_type=ERC20&sell_token_address=0xccc8cb5229b0ac8069c51fd58367fd1e622afd97"
                elif sell_address == "IMX":
                    sell_info_str = sell_info_str + "&sell_token_type=ERC20&sell_token_address=0xf57e7e7c23978c3caec3c3548e3d615c346e79ff"
                elif sell_address == "USDC":
                    sell_info_str = sell_info_str + "&sell_token_type=ERC20&sell_token_address=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
                elif sell_address == "GOG":
                    sell_info_str = sell_info_str + "&sell_token_type=ERC20&sell_token_address=0x9ab7bb7fdc60f4357ecfef43986818a2a3569c62"
                elif sell_address == "OMI":
                    sell_info_str = sell_info_str + "&sell_token_type=ERC20&sell_token_address=0xed35af169af46a02ee13b9d79eb57d6d68c1749e"
                elif (split_sell_address[0] == "NFT"):
                    sell_info_str = sell_info_str + "&sell_token_address=" + str(split_sell_address[1])
                else:
                    raise Exception(f"What else is this sell_address? {sell_address}")

        status_str = ""
        if input_status_str:
            status_str = "&status=" + input_status_str.lower()


        time_str = ""
        if time_tuple:
            from_time_stamp_str = time_tuple[0]
            to_time_stamp_str = time_tuple[1]
            time_str = "&updated_min_timestamp=" + from_time_stamp_str + "&updated_max_timestamp=" + to_time_stamp_str


        buy_meta_data_str = ""
        sell_meta_data_str = ""
        if meta_data_dic:
            if "sell_address" in token_address_dic:
                split_sell_address = sell_address.split("_")
                if split_sell_address[0] == "NFT":
                    sell_meta_data_str = "&sell_metadata=" + Metadata_Creator.encode_meta_data_dic(meta_data_dic["sell"])

            if "buy_address" in token_address_dic:
                split_buy_address = buy_address.split("_")
                if split_buy_address[0] == "NFT":
                    buy_meta_data_str = "&buy_metadata=" + Metadata_Creator.encode_meta_data_dic(meta_data_dic["buy"])


        final_url = cls._base_url + "/orders?page_size=200&order_by=updated_at&direction=asc" + status_str + time_str + buy_info_str + buy_meta_data_str + sell_info_str + sell_meta_data_str

        return final_url

    @classmethod
    def create_url_by_collection_address(cls, collection_address):
        url = cls._base_url + "/collections?page_size=200" + str(collection_address)
        return url

    @classmethod
    def create_url_by_order_id(cls, order_id):
        url = cls._base_url + "/orders/" + str(order_id) + "?include_fees=true"
        return url

    @classmethod
    def create_url_by_sell_token_id(cls, token_id):
        url = cls._base_url + "/orders?page_size=200&sell_token_id=" + str(token_id)
        return url


    @classmethod
    def create_url_of_order_by_user_status_sell_token_id(cls, user_str, status_str, sell_token_id_str):
        url = cls._base_url + "/orders?page_size=200&user=" + user_str + "&status=" + status_str.lower() + "&sell_token_id=" + sell_token_id_str
        return url

    @classmethod
    def create_url_of_order_by_user_status_buy_token_id(cls, user_str, status_str, sell_token_id_str):
        url = cls._base_url + "/orders?page_size=200&status=" + status_str.lower() + "&buy_token_id=" + sell_token_id_str
        return url
