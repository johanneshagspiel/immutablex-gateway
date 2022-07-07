import concurrent.futures
import traceback
import time
from datetime import datetime
from src.objects.inventory.inventorymanager import InventoryManager
from src.objects.orders.gods_unchained.orderadministratorgu import OrderAdministratorGU
from src.operators.client import Client
from src.operators.helpers.competitionhandler import CompetitionHandler
from src.operators.tradeclassifier import TradeClassifier
from src.operators.transfersupervisor import TransferSupervisor
from src.scrappers.coinapiscrapper import CoinAPIScrapper
from src.scrappers.coinmarketcapscrapper import CoinMarketCapScrapper
from src.scrappers.godsunchainedpoller import GodsUnchainedPoller
from src.util.custom_exceptions import TooManyAPICalls, ResponseError, RequestError, InternalServerError, \
    StartNewDayError
from src.util.files.filehandler import FileHandler
from src.util.files.fileiohelper import FileIoHelper
from src.util.helpers import SafeDatetimeConverter, FutureHelper
from src.util.numberconverter import NumberConverter


class ParallelCardSupervisor:
    """
    A class to supervise multiple cards in parallel
    """

    def __init__(self):
        """
        The constructor of the ParallelCardSupervisor class
        """
        self._ts = TransferSupervisor()
        self.keep_going = True

        self.inventory_list = []
        self.balance = {}

        self.executor = None

        self.active_updated_orders_df = None
        self.last_active_updated_orders_timestamp = None

        self.sold_order_list = []
        self._future_list = []


    def parallel_supervise_inventory(self, input_inventory_list, start_active_updated_orders_df, start_balance):
        """
        A method to parallel supervise cards
        :param input_inventory_list: the list of cards curently in the inventory
        :param start_active_updated_orders_df: the start active updated orders DataFrame
        :param start_balance: the start token balance
        :return: None
        """
        connections = 1000

        print("Supervising inventory")
        self.inventory_list = input_inventory_list

        self.active_updated_orders_df = start_active_updated_orders_df
        self.last_active_updated_orders_timestamp = datetime.utcnow()

        self.balance = {}
        self.balance["ETH"] = start_balance["ETH"]["cash"]["tokens"]
        self.balance["GODS"] = start_balance["GODS"]["cash"]["tokens"]

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=connections)

        for inventory_entry in input_inventory_list:
            temp_future = self.executor.submit(self.start_supervising_entry, inventory_entry)
            self._future_list.append(temp_future)

        #self.executor.submit(self.start_supervising_updated_sell_orders)

        while FutureHelper.at_least_one_future_not_done(self._future_list):

            # eth_balance = self.balance["ETH"]
            # gods_balance = self.balance["GODS"]
            #
            # if eth_balance > 0:
            #     self.make_use_of_surplus_tokens(currency="ETH", token_amount=eth_balance)
            #
            # if gods_balance > 0:
            #     self.make_use_of_surplus_tokens(currency="GODS", token_amount=gods_balance)

            time.sleep(1)

    def start_supervising_updated_sell_orders(self):
        """
        A method to start supervising updated sell orders
        :return: None
        """

        last_change_time_stamp = FileIoHelper.read_updated_active_sell_orders_timestamp()

        while True:

            not_yet_accessed = True
            while not_yet_accessed:
                try:
                    current_change_time_stamp = FileIoHelper.read_updated_active_sell_orders_timestamp()
                    not_yet_accessed = False
                except PermissionError:
                    time.sleep(1)

            if current_change_time_stamp != last_change_time_stamp:

                not_yet_loaded = True
                while not_yet_loaded:
                    try:
                        new_active_updated_orders_df = OrderAdministratorGU.create_active_updated_orders_df("SELL")
                        not_yet_loaded = False
                    except PermissionError:
                        time.sleep(1)
                print("DF updated")
                self.active_updated_orders_df = new_active_updated_orders_df
                self.last_active_updated_orders_timestamp = datetime.utcnow()

            last_change_time_stamp = current_change_time_stamp
            time.sleep(1)

    def start_supervising_entry(self, inventory_entry):
        """
        A method called before supervising inventory entries to check the competition file
        :param inventory_entry: the card to be supervised
        :return: None
        """

        inventory_entry, competition_price_dic = CompetitionHandler.check_competition_file_of_inventory_entry(inventory_entry)
        self._supervise_entry(inventory_entry, competition_price_dic)

    def _supervise_entry(self, inventory_entry, competition_price_dic):
        """
        A method to supervise a card
        :param inventory_entry: the inventory entry of a card
        :param competition_price_dic: the expected prices from the competitors
        :return: None
        """

        bot_counter = 0
        bot_mode_on = False

        start_sleep = 10
        sleep_amount = start_sleep

        historical_price_dic = CoinAPIScrapper.get_historical_prices()
        current_price_dic = CoinMarketCapScrapper.get_latest_currency_price()

        start_time = datetime.now()
        times_checked = 0
        is_not_sold = True

        last_timestamp_change = None
        gp = GodsUnchainedPoller()

        while self.keep_going and is_not_sold:

            try:

                inventory_entry_is_sold, potential_latest_filled_order = InventoryManager.check_if_inventory_entry_is_sold(inventory_entry, historical_price_dic)

                now = datetime.now()
                difference = (now - start_time).total_seconds() - (times_checked * 300)

                if (difference > 300):
                    times_checked = times_checked + 1
                    current_price_dic = CoinMarketCapScrapper.get_latest_currency_price()

                if inventory_entry_is_sold:
                    currency_sale_price = NumberConverter.get_float_from_quantity_decimal(potential_latest_filled_order.quantity, potential_latest_filled_order.decimals)
                    currency_price_euro_at_sale = current_price_dic[potential_latest_filled_order.currency] * currency_sale_price
                    print(f"\"{potential_latest_filled_order.card_name}\" was sold for {currency_sale_price} {potential_latest_filled_order.currency} or {currency_price_euro_at_sale:.3f} EUR")

                    prev_balance = self.balance[potential_latest_filled_order.currency]
                    new_balance = prev_balance + currency_sale_price
                    self.balance[potential_latest_filled_order.currency] = new_balance

                    new_inventory_list = InventoryManager.update_inventory_list_based_on_sold_order(potential_latest_filled_order, inventory_entry, self.inventory_list)
                    self.inventory_list = new_inventory_list
                    is_not_sold = False

                else:

                    # if bot_mode_on:
                    #     all_cards_available = gp._get_all_active_sell_jsons_for_a_currency_and_quality(asset_name=inventory_entry.card_name, currency_string=inventory_entry.sale_currency, quality=inventory_entry.card_quality)
                    #
                    # else:
                    #     wait_for_new_df = True
                    #     start_time_wait = datetime.utcnow()
                    #
                    #     while wait_for_new_df:
                    #
                    #         if self.last_active_updated_orders_timestamp != last_timestamp_change:
                    #             print("New DF Detected")
                    #             current_df = self.active_updated_orders_df
                    #             last_timestamp_change = self.last_active_updated_orders_timestamp
                    #             all_cards_available = current_df[(current_df["card_name"] == inventory_entry.card_name) & (current_df["currency"] == inventory_entry.sale_currency) & (current_df["card_quality"] == inventory_entry.card_quality)]
                    #             wait_for_new_df = False
                    #         else:
                    #             current_time = datetime.utcnow()
                    #             seconds_of_waiting = (current_time - start_time_wait).total_seconds()
                    #
                    #             if seconds_of_waiting >= 300:
                    #                 all_cards_available = gp._get_all_active_sell_jsons_for_a_currency_and_quality(asset_name=inventory_entry.card_name, currency_string=inventory_entry.sale_currency, quality=inventory_entry.card_quality)
                    #                 wait_for_new_df = False

                    # wait_for_new_df = True
                    #
                    # while wait_for_new_df:
                    #
                    #     if self.last_active_updated_orders_timestamp != last_timestamp_change:
                    #         print("New DF Detected")
                    #         current_df = self.active_updated_orders_df
                    #         last_timestamp_change = self.last_active_updated_orders_timestamp
                    #         all_cards_available = current_df[(current_df["card_name"] == inventory_entry.card_name) & (current_df["currency"] == inventory_entry.sale_currency) & (current_df["card_quality"] == inventory_entry.card_quality)]
                    #         wait_for_new_df = False

                    all_cards_available = gp._get_all_active_sell_jsons_for_a_currency_and_quality(asset_name=inventory_entry.card_name, currency_string=inventory_entry.sale_currency,quality=inventory_entry.card_quality)

                    msg_list = self._ts.supervise_card(inventory_entry, all_cards_available, current_price_dic, competition_price_dic)

                    msg_card_name, msg_token_id, new_competition_price_dic, msg_time, msg_instruction, msg_text = msg_list
                    msg_time_str = SafeDatetimeConverter.datetime_to_string(msg_time)

                    print_string = f"{msg_time_str}\t\t\"{msg_card_name}\" {msg_token_id}\t\t{msg_text}"
                    print(print_string)

                    if msg_instruction == "fast":
                        bot_mode_on = True
                        bot_counter = 5
                        sleep_amount = start_sleep

                    if bot_mode_on:
                        bot_counter = bot_counter - 1
                        time.sleep(3)

                        if bot_counter == 0:
                            bot_mode_on = False
                            sleep_amount = start_sleep

                    else:
                        if msg_instruction == "slow":
                            time.sleep(sleep_amount)

                            if sleep_amount < 120:
                                sleep_amount = sleep_amount + 30

                    competition_price_dic = new_competition_price_dic

            except StartNewDayError as start_new_day_error:
                historical_price_dic = CoinAPIScrapper.get_historical_prices()

            except (ResponseError, RequestError, TooManyAPICalls, InternalServerError) as custom_error:
                time.sleep(2)

            except Exception as e:
                traceback.print_exc()
                is_not_sold = False

        else:
            print(f"Shutting down {inventory_entry.card_name}")

    def make_use_of_surplus_tokens(self, currency, token_amount):
        """
        A method to use the suruplus token to purchase cards
        :param currency: the currency to purchase cards in
        :param token_amount: the current amount of tokens available
        :return: None
        """

        if currency == "ETH":
            purchase_currency = "ETH"
            sale_currency = "GODS"
            cheapest_currency_1 = "cheapest_ETH"
            cheapest_currency_2 = "cheapest_GODS"
            currency_1_order_id = "ETH_order_id"

        elif currency == "GODS":
            purchase_currency = "GODS"
            sale_currency = "ETH"
            cheapest_currency_1 = "cheapest_GODS"
            cheapest_currency_2 = "cheapest_ETH"
            currency_1_order_id = "GODS_order_id"

        risk_level_list = [1, 2]

        for risk_level in risk_level_list:
            print(f"Purchasing {purchase_currency} cards with risk_level {risk_level}")
            if risk_level == 1:
                overall_classification_df, classification_dic = TradeClassifier.create_df_of_orders_type_1(purchase_currency=purchase_currency, sale_currency=sale_currency, inventory_list=self.inventory_list)

            elif risk_level == 2:
                overall_classification_df, classification_dic = TradeClassifier.create_df_of_orders_type_2(purchase_currency=purchase_currency, sale_currency=sale_currency, inventory_list=self.inventory_list)

            # elif risk_level == 3:
            #     overall_classification_df, classification_dic = TradeClassifier.create_df_of_orders_type_3(purchase_currency=purchase_currency, sale_currency=sale_currency, inventory_list=self.inventory_list)
            #
            # elif risk_level == 4:
            #     overall_classification_df, classification_dic = TradeClassifier.create_df_of_orders_type_4(purchase_currency=purchase_currency, sale_currency=sale_currency, inventory_list=self.inventory_list)

            classification_df = overall_classification_df[overall_classification_df[cheapest_currency_1] <= token_amount]

            test_folder = FileHandler.get_base_path("test_directory")
            classification_file_path = str(test_folder) + "\\" + str(purchase_currency) + "_to_" + str(sale_currency) + "_level_" + str(risk_level) + "_classification.csv"
            classification_df.to_csv(classification_file_path, index=False)


            while len(classification_df) > 0 and token_amount > 0:

                row_index_max_t_dif = classification_df["t_dif"].idxmax()
                row_max_t_dif = classification_df.loc[row_index_max_t_dif]

                purchase_order_id = row_max_t_dif[currency_1_order_id]

                error_encountered, result_order, remove_order_from_contention = Client._automatically_purchase_card(purchase_order_id=purchase_order_id, sale_currency=sale_currency, classification_dic=classification_dic)

                if error_encountered:
                    if result_order:
                        OrderAdministratorGU.receive_purchase_error_order(result_order)

                else:

                    new_inventory_entry = InventoryManager.create_new_inventory_entry_purchased_now(order_object=result_order, currency_to_sell_in=sale_currency)
                    InventoryManager.add_new_inventory_entry_to_file(new_inventory_entry)

                    purchase_price_currency_float = NumberConverter.get_float_from_quantity_decimal(quantity=result_order.quantity, decimals=result_order.decimals)
                    token_amount = token_amount - purchase_price_currency_float
                    self.balance[purchase_currency] = token_amount

                    print(f"\"{result_order.card_name}\" purchased successfully for {purchase_price_currency_float} - new remaining token balance: {token_amount}.")

                    testing_info_dic = {}
                    testing_info_dic["token_id"] = result_order.token_id
                    testing_info_dic["card_name"] = result_order.card_name
                    testing_info_dic["classification_dic"] = classification_dic
                    FileIoHelper.add_testing_info_dic(testing_info_dic)

                    temp_future = self.executor.submit(self.start_supervising_entry, new_inventory_entry)
                    self._future_list.append(temp_future)

                if remove_order_from_contention:
                    classification_df = classification_df.drop(row_index_max_t_dif)

        print(f"After all cards available have been purchased, the new remaining token balance is {token_amount}.")
