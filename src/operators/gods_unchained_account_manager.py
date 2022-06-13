from objects.orders.gods_unchained.order_administrator_gu import Order_Administrator_GU
from objects.currency.currency import Currency_Info_Dic
from objects.inventory.inventory_manager import Inventory_Manager
from operators.client import Client
from operators.trade_classifier import Trade_Classifier
from operators.trading_manager import Trading_Manager
from scrappers.coinmarketcap_scrapper import CoinMarketCap_Scrapper
from util.files.file_handler import File_Handler
from util.number_converter import Number_Converter



class Gods_Unchained_Account_Manager():

    def __init__(self):
        self._trading_manager = Trading_Manager()
        self.client = Client()

    def get_inventory_list(self):
        inventory_list = Inventory_Manager.get_inventory_list()
        checked_inventory_list = Inventory_Manager.check_inventory_list(inventory_list)
        return checked_inventory_list


    def purchase_card(self, purchase_order_id, currency_to_sell_in):

        filled_order = self.client.purchase_card(purchase_order_id=purchase_order_id)

        if filled_order:
            new_inventory_entry = Inventory_Manager.create_new_inventory_entry_purchased_now(filled_order, currency_to_sell_in)
            Inventory_Manager.add_new_inventory_entry_to_file(new_inventory_entry)

    def test(self):
        result_df, dic = Trade_Classifier.create_df_of_orders_type_5(inventory_list=self.get_inventory_list(), purchase_currency="GODS", sale_currency="ETH")

        test_directory_path = File_Handler.get_base_path("test_directory")
        test_file_path = str(test_directory_path) + "//test.csv"
        result_df.to_csv(test_file_path, index=False)


    def get_balance(self):

        latest_currency_price_dic = CoinMarketCap_Scrapper.get_latest_currency_price()

        client = Client()
        token_balance_list = client.get_token_balance_of_user()

        new_balance_dic = {}

        for token_dic in token_balance_list:
            symbol = token_dic["symbol"]
            quantity = int(token_dic["balance"])
            decimals = Currency_Info_Dic.get[symbol]["decimals"]
            tokens = Number_Converter.get_float_from_quantity_decimal(quantity=quantity, decimals=decimals)
            euro_value = tokens * latest_currency_price_dic[symbol]

            new_balance_dic[symbol] = {}
            new_balance_dic[symbol]["total"] = {}
            new_balance_dic[symbol]["cash"] = {}

            new_balance_dic[symbol]["cash"]["tokens"] = tokens
            new_balance_dic[symbol]["cash"]["euro"] = euro_value

            new_balance_dic[symbol]["total"]["tokens"] = tokens
            new_balance_dic[symbol]["total"]["euro"] = euro_value



        for inventory_entry in self.inventory_list:
            currency = inventory_entry.purchase_currency
            tokens = float(inventory_entry.purchase_price_currency)
            euro_value = tokens * latest_currency_price_dic[currency]

            new_balance_dic[currency]["cards"] = {}

            new_balance_dic[currency]["cards"]["tokens"] = tokens
            new_balance_dic[currency]["cards"]["euro"] = euro_value

            prev_tokens = new_balance_dic[currency]["total"]["tokens"]
            total_tokens = prev_tokens + tokens
            new_balance_dic[currency]["total"]["tokens"] = total_tokens

            prev_euro = new_balance_dic[currency]["total"]["euro"]
            total_euro = prev_euro + euro_value
            new_balance_dic[currency]["total"]["euro"] = total_euro

        return new_balance_dic



    ####

    def run(self):

        self.inventory_list = self.get_inventory_list()
        self.balance_dic = self.get_balance()
        self._trading_manager.supervise_inventory_list(self.inventory_list, self.balance_dic)
