from src.objects.currency.currency import CurrencyInfoDic
from src.objects.inventory.inventorymanager import InventoryManager
from src.operators.client import Client
from src.operators.tradeclassifier import TradeClassifier
from src.operators.tradingmanager import TradingManager
from src.scrappers.coinmarketcapscrapper import CoinMarketCapScrapper
from src.util.files.filehandler import FileHandler
from src.util.numberconverter import NumberConverter



class GodsUnchainedAccountManager:
    """
    A class to automatically trade God Unchained cards
    """

    def __init__(self):
        """
        The constructor of the GodsUnchainedAccountManager class
        """
        self._trading_manager = TradingManager()
        self.client = Client()

    def get_inventory_list(self):
        """
        A method to get an updated and checked inventory list
        :return: inventory list
        """
        inventory_list = InventoryManager.get_inventory_list()
        checked_inventory_list = InventoryManager.check_inventory_list(inventory_list)
        return checked_inventory_list

    def purchase_card(self, purchase_order_id, currency_to_sell_in):
        """
        A method purchase a card
        :param purchase_order_id: the order id of the card to be purchased
        :param currency_to_sell_in: the currency to sell the card in
        :return: None
        """

        filled_order = self.client.purchase_card(purchase_order_id=purchase_order_id)

        if filled_order:
            new_inventory_entry = InventoryManager.create_new_inventory_entry_purchased_now(filled_order, currency_to_sell_in)
            InventoryManager.add_new_inventory_entry_to_file(new_inventory_entry)

    def get_balance(self):
        """
        A method to get the latest token balance
        :return: the token balance as a dictionary
        """

        latest_currency_price_dic = CoinMarketCapScrapper.get_latest_currency_price()

        client = Client()
        token_balance_list = client.get_token_balance_of_user()

        new_balance_dic = {}

        for token_dic in token_balance_list:
            symbol = token_dic["symbol"]
            quantity = int(token_dic["balance"])
            decimals = CurrencyInfoDic.information_dic[symbol]["decimals"]
            tokens = NumberConverter.get_float_from_quantity_decimal(quantity=quantity, decimals=decimals)
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

    def run(self):
        """
        A method to run the automated trading loop
        :return: None
        """

        self.inventory_list = self.get_inventory_list()
        self.balance_dic = self.get_balance()
        self._trading_manager.supervise_inventory_list(self.inventory_list, self.balance_dic)
