import json
import time
from src.objects.currency.currency import Currency
from src.scrappers.coinmarketcapscrapper import CoinMarketCapScrapper
from src.scrappers.godsunchainedpoller import GodsUnchainedPoller
from src.scrappers.safe_GodsUnchainedPoller import Safe_GodsUnchainedPoller
from src.util.files.filehandler import FileHandler
from src.util.imxpy.imx_client import IMXClient
from src.util.imxpy.imx_objects import CancelOrderParams, CreateOrderParams, ERC721, ERC20, ETH, CreateTradeParams, \
    TransferParams
from src.util.numberconverter import NumberConverter


class Client:
    """
    A class to interact with the IMX blockchain i.e. by buying cards or making sell offers
    """

    pk_info_file_path = FileHandler.get_base_path("pk_info_file")
    with open(pk_info_file_path, 'r', encoding='utf-8') as pk_info_file:
        pk_info_dic = json.load(pk_info_file)
    pk_info_file.close()

    temp_sender = pk_info_dic["sender"]
    if len(temp_sender) == 0:
        raise Exception("No address of the account on IMX was found - add it to resources/client_info/pk_info.json")
    else:
        _sender = temp_sender

    temp_pk = pk_info_dic["pk"]
    if len(temp_pk) == 0:
        raise Exception("No private key of the wallet was found - add it to resources/client_info/pk_info.json")
    else:
        imx_client = IMXClient(net="main", n_workers=32, pk=temp_pk)

    def __init__(self):
        """
        The constructor of the Client class
        """
        pass

    @classmethod
    def get_the_token_id_of_all_assets_of_user(cls):
        """
        A method to get the token ids of all assets owned by the user
        :return: a list of token ids
        """
        result = Client.imx_client.db.assets(user=Client._sender)

        if "remaining" in result or "cursors" in result:
            raise Exception("Somehow getting the token id of all assets is not spread over multiple pages")

        token_id_list = [entry["token_id"] for entry in result]
        return token_id_list

    @classmethod
    def get_list_of_all_tokens_that_exist(cls):
        """
        A method to get all tokens that exist on IMX.
        :return: a list all tokens and associated information
        """
        res = Client.imx_client.db.tokens()
        result = res["result"]
        return result

    @classmethod
    def get_token_balance_of_user(cls):
        """
        A method to get the current token balance of the user
        :return: the current token balance
        """
        res = Client.imx_client.db.balances(owner=Client._sender)
        result = res["result"]
        return result

    @classmethod
    def transfer_card(cls, receiver_address, token_id):
        """
        A method to transfer a card to another user
        :param receiver_address: the address of the receiver
        :return: None
        """

        transfer_card = ERC721(contract_addr="0xacb3c6a43d15b907e8433077b6d38ae40936fe2c", token_id=token_id)

        transfer_params = TransferParams(sender=Client.pk_info_dic["sender"], receiver=receiver_address,
                                         token=transfer_card)
        future = Client.imx_client.transfer(transfer_params)
        print(future)

    @classmethod
    def get_trade_with_buy_token_id_and_min_timestamp(cls, buy_token_id, min_timestamp_str):
        """
        A method to get all trades associated with a token id after a timestamp
        :param buy_token_id: the token id of the purchased card
        :param min_timestamp_str: the minimum timestamp
        :return: a list of trades
        """
        res = Client.imx_client.db.trades(party_b_token_id=buy_token_id, min_timestamp=min_timestamp_str)
        result = res["result"]
        return result

    @classmethod
    def cancel_order(cls, order_id):
        """
        A method to cancel an order based on order id
        :param order_id: the order id
        :return: None
        """
        cancel_params = CancelOrderParams(order_id=order_id)
        future = Client.imx_client.cancel_order(cancel_params)
        res = future.result()
        print(res)

        Client.imx_client.db.stark_key()

    @classmethod
    def create_sell_order(cls, sell_card_token_id, currency_str, price_as_str):
        """
        A method to create a sell order
        :param sell_card_token_id: the token id of the card to be sold
        :param currency_str: the currency in which to sell the card in
        :param price_as_str: the sale price
        :return: boolean whether offering the card worked
        """

        card_to_sell = ERC721(contract_addr="0xacb3c6a43d15b907e8433077b6d38ae40936fe2c",
                              token_id=str(sell_card_token_id))

        currency_enum = Currency[currency_str]

        if currency_enum == Currency.GODS:
            buy_demand = ERC20(symbol="GODS", contract_addr="0xccc8cb5229b0ac8069c51fd58367fd1e622afd97",
                               quantity=price_as_str)
        elif currency_enum == Currency.ETH:
            buy_demand = ETH(quantity=price_as_str)

        create_order_params = CreateOrderParams(sender=Client._sender, token_sell=card_to_sell,
                                                token_buy=buy_demand)

        future = Client.imx_client.create_order(create_order_params)

        res = future.result()

        success = res["status"] == "success"

        if not success:
            if "result" in res:
                if res["result"] == '[TYPESCRIPTWRAPPER]: Rated limited':
                    pass
                elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4039 Errcode: ETIMEDOUT':
                    pass
                elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4058 Errcode: ENOENT':
                    pass
                elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4077 Errcode: ECONNRESET':
                    pass
                elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4079 Errcode: ECONNABORTED':
                    pass
                elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -3008 Errcode: ENOTFOUND':
                    pass
                elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4092 Errcode: EACCES':
                    pass
                else:
                    print(res)

        if success:
            time.sleep(3)

        return success

    @classmethod
    def purchase_card(cls, purchase_order_id):
        """
        A method purchase a card
        :param purchase_order_id: the order id of the card to be purchased
        :return: None
        """

        gp = GodsUnchainedPoller()
        order = gp.get_order_by_order_id(purchase_order_id)

        current_status = order.status

        if current_status != "active":
            print(f"This card is no longer available but now it is {current_status}")

        else:
            price_as_str = NumberConverter.get_float_str_from_quantity_decimal(quantity=order.quantity,
                                                                               decimals=order.decimals)
            price_as_float = NumberConverter.get_float_from_quantity_decimal(quantity=order.quantity,
                                                                             decimals=order.decimals)

            currency_prices_dic = CoinMarketCapScrapper.get_now_currency_price()

            price_euro = price_as_float * currency_prices_dic[order.currency]

            print(f"Do you want to spend {price_euro:.3f} EUR or {price_as_float:.3f} {order.currency} "
                  f"to purchase \"{order.card_name}\"? Type yes to purchase.")

            answer = input()

            if answer == "yes":

                card_to_buy = ERC721(contract_addr="0xacb3c6a43d15b907e8433077b6d38ae40936fe2c",
                                     token_id=str(order.token_id))

                if order.currency == "GODS":
                    purchase_offer = ERC20(symbol="GODS", contract_addr="0xccc8cb5229b0ac8069c51fd58367fd1e622afd97",
                                           quantity=price_as_str)
                elif order.currency == "ETH":
                    purchase_offer = ETH(quantity=price_as_str)

                create_trade_params = CreateTradeParams(order_id=purchase_order_id, sender=Client._sender,
                                                        token_sell=purchase_offer, token_buy=card_to_buy)
                future = Client.imx_client.create_trade(create_trade_params)

                res = future.result()
                success = res["status"] == 'success'

                if success:

                    time.sleep(5)
                    new_order = gp.get_order_by_order_id(purchase_order_id)

                    if new_order.status == "filled":
                        print(f"\"{new_order.card_name}\" purchased successfully!")
                        return new_order

                    else:
                        print(f"Something went wrong with purchasing order {purchase_order_id}")
                        print(json.dumps(new_order.to_print_dic(), indent=4))

                else:
                    print(res)
                    print("The purchase did potentially not happen")

    @classmethod
    def _automatically_purchase_card(cls, purchase_order_id, sale_currency, classification_dic):
        """
        A method to automate the purchasing process
        :param purchase_order_id: the order id of the card to be purchased
        :param sale_currency: the currency in which to sell the card
        :param classification_dic: dictionary with information to determine whether the purchase should happen i.e. the
        minimal amount of profit expected
        :return: Boolean representing the purchase has failed, either an Order or None, Boolean representing whether
        the purchase should be attempted again
        """

        additional_info_dic_1 = {}
        additional_info_dic_1["order_id"] = purchase_order_id
        order = Safe_GodsUnchainedPoller.safe_download(task="get_order_by_order_id",
                                                         information_dic=additional_info_dic_1)

        current_status = order.status

        if current_status != "active":
            return True, order, True

        else:

            if "min_profit_span" in classification_dic:
                min_profit_span = classification_dic["min_profit_span"]
            else:
                raise Exception("Implement how the orders were classified")

            if "quality" in classification_dic:

                additional_info_dic_2 = {}

                additional_info_dic_2["asset_name"] = order.card_name
                additional_info_dic_2["currency_string"] = sale_currency
                additional_info_dic_2["quality"] = classification_dic["quality"]

                other_orders_list = Safe_GodsUnchainedPoller.safe_download(
                    task="get_all_active_sell_orders_for_a_currency_and_quality",
                    information_dic=additional_info_dic_2)

            else:
                raise Exception("Implement how the orders were classified")

            currency_price_float_list = [NumberConverter.get_float_from_quantity_decimal(
                quantity=other_order.quantity,
                decimals=other_order.decimals) for other_order in other_orders_list]

            currency_price_float_list.sort()
            min_sale_price_currency_float = currency_price_float_list[0]

            current_currency_dic = CoinMarketCapScrapper.get_now_currency_price()
            min_sale_price_euro_float = current_currency_dic[sale_currency] * min_sale_price_currency_float
            purchase_price_euro_float = current_currency_dic[order.currency] * \
                                        NumberConverter.get_float_from_quantity_decimal(quantity=order.quantity,
                                                                                        decimals=order.decimals)

            if min_sale_price_euro_float >= (min_profit_span * purchase_price_euro_float):

                price_as_str = NumberConverter.get_float_str_from_quantity_decimal(quantity=order.quantity,
                                                                                   decimals=order.decimals)

                card_to_buy = ERC721(contract_addr="0xacb3c6a43d15b907e8433077b6d38ae40936fe2c",
                                     token_id=str(order.token_id))

                if order.currency == "GODS":
                    purchase_offer = ERC20(symbol="GODS", contract_addr="0xccc8cb5229b0ac8069c51fd58367fd1e622afd97",
                                           quantity=price_as_str)
                elif order.currency == "ETH":
                    purchase_offer = ETH(quantity=price_as_str)

                create_trade_params = CreateTradeParams(order_id=purchase_order_id, sender=Client._sender,
                                                        token_sell=purchase_offer, token_buy=card_to_buy)

                future = Client.imx_client.create_trade(create_trade_params)

                res = future.result()
                success = res["status"] == 'success'

                if success:
                    time.sleep(5)

                    additional_info_dic_3 = {}
                    additional_info_dic_3["order_id"] = purchase_order_id
                    new_order = Safe_GodsUnchainedPoller.safe_download(task="get_order_by_order_id",
                                                                         information_dic=additional_info_dic_3)

                    if new_order.status == "filled":
                        return False, new_order, True

                    else:
                        print(f"Something went wrong with purchasing order {purchase_order_id}.")
                        print(json.dumps(new_order.to_print_dic(), indent=4))
                        return True, None, False

                else:
                    if "result" in res:
                        if res["result"] == '[TYPESCRIPTWRAPPER]: Rated limited':
                            pass
                        elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4039 Errcode: ETIMEDOUT':
                            pass
                        elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4058 Errcode: ENOENT':
                            pass
                        elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4077 Errcode: ECONNRESET':
                            pass
                        elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4079 Errcode: ECONNABORTED':
                            pass
                        elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -3008 Errcode: ENOTFOUND':
                            pass
                        elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4092 Errcode: EACCES':
                            pass

                        else:
                            print(res)
                    else:
                        print(res)

                    print("The purchase did potentially not happen.")
                    return True, None, False

            else:
                print(f"The purchase of \"{order.card_name}\" is no longer profitable.")
                return True, None, True
