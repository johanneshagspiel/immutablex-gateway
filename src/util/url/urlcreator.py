from src.util.url.metadata_creator import MetaDataCreator


class UrlCreator:
    """
    A class to create urls for requests
    """
    _base_url = "https://api.x.immutable.com/v1"

    def __init__(self):
        """
        The constructor of the UrlCreator class
        """
        pass

    @staticmethod
    def create_next_cursor_url(url, next_cursor_url):
        """
        A method to create the next url based on a cursor
        :param url: the previous url
        :param next_cursor_url: the cursor to the next url
        :return: the resulting url
        """

        base_url = str(url.split("page_size=200")[0]) + "page_size=200"
        rest_url = url.split("page_size=200")[1]

        next_url = base_url + "&cursor=" + next_cursor_url + "&" + rest_url

        return next_url

    @classmethod
    def create_url_by_order_type(cls, input_status_str, token_address_dic, time_tuple, meta_data_dic):
        """
        A method to create an url based on order characteristics
        :param input_status_str: the status of the order
        :param token_address_dic: the addresses of the users involved
        :param time_tuple: the to- and from timestamp
        :param meta_data_dic: a dictionary of metadata information
        :return: an url
        """

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
                    sell_meta_data_str = "&sell_metadata=" + MetaDataCreator.encode_meta_data_dic(meta_data_dic["sell"])

            if "buy_address" in token_address_dic:
                split_buy_address = buy_address.split("_")
                if split_buy_address[0] == "NFT":
                    buy_meta_data_str = "&buy_metadata=" + MetaDataCreator.encode_meta_data_dic(meta_data_dic["buy"])

        final_url = cls._base_url + "/orders?page_size=200&order_by=updated_at&direction=asc" + status_str + time_str + buy_info_str + buy_meta_data_str + sell_info_str + sell_meta_data_str

        return final_url

    @classmethod
    def create_url_by_collection_address(cls, collection_address):
        """
        A method to create url based on a collection address
        :param collection_address: the collections address
        :return: the resulting url
        """
        url = cls._base_url + "/collections?page_size=200" + str(collection_address)
        return url

    @classmethod
    def create_url_by_order_id(cls, order_id):
        """
        A method to create an url based on order id
        :param order_id: the order id
        :return: the resulting url
        """
        url = cls._base_url + "/orders/" + str(order_id) + "?include_fees=true"
        return url

    @classmethod
    def create_url_by_sell_token_id(cls, token_id):
        """
        A method to create an url based on sell token id
        :param token_id: the token id of the order to be downloaded
        :return: the resulting url
        """
        url = cls._base_url + "/orders?page_size=200&sell_token_id=" + str(token_id)
        return url

    @classmethod
    def create_url_of_order_by_user_status_sell_token_id(cls, user_str, status_str, sell_token_id_str):
        """
        A method to create an url based on a users address, status and buy token id
        :param user_str: the user address
        :param status_str: the status of the order
        :param sell_token_id_str: the token id
        :return: the resulting url
        """
        url = cls._base_url + "/orders?page_size=200&user=" + user_str + "&status=" + status_str.lower() + "&sell_token_id=" + sell_token_id_str
        return url

    @classmethod
    def create_url_of_order_by_user_status_buy_token_id(cls, user_str, status_str, sell_token_id_str):
        """
        A method to create an url based on a users address, status and buy token id
        :param user_str: the users waller
        :param status_str: the status of the order
        :param sell_token_id_str: the buy token id
        :return: the resulting id
        """
        url = cls._base_url + "/orders?page_size=200&status=" + status_str.lower() + "&buy_token_id=" + sell_token_id_str
        return url
