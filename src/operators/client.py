import json
import time
from src.objects.currency.currency import Currency
from src.scrappers.coinmarketcap_scrapper import CoinMarketCap_Scrapper
from src.scrappers.gods_unchained_poller import Gods_Unchained_Poller
from src.scrappers.safe_gods_unchained_poller import Safe_Gods_Unchained_Poller
from src.util.files.file_handler import File_Handler
from src.util.imxpy.imx_client import IMXClient
from src.util.imxpy.imx_objects import CancelOrderParams, CreateOrderParams, ERC721, ERC20, ETH, CreateTradeParams, TransferParams
from src.util.number_converter import Number_Converter


class Client():

    pk_info_file_path = File_Handler.get_base_path("pk_info_file")
    with open(pk_info_file_path, 'r', encoding='utf-8') as pk_info_file:
        pk_info_dic = json.load(pk_info_file)
    pk_info_file.close()

    temp_sender = pk_info_dic["sender"]
    if len(temp_sender) == 0:
        raise Exception("No address of the account on Immutable X was found - add it to resources/client_info/pk_info.json")
    else:
        _sender = temp_sender

    temp_pk = pk_info_dic["pk"]
    if len(temp_pk) == 0:
        raise Exception("No private key of the wallet was found - add it to resources/client_info/pk_info.json")
    else:
        imx_client = IMXClient(net="main", n_workers=32, pk=temp_pk)


    def __init__(self):
        None


    @classmethod
    def get_the_token_id_of_all_assets_of_user(cls):
        result = Client.imx_client.db.assets(user=Client._sender)

        if "remaining" in result or "cursors" in result:
            raise Exception("Somehow getting the token id of all assets is not spread over multiple pages")

        token_id_list = [entry["token_id"] for entry in result]
        return token_id_list

    @classmethod
    def get_list_of_all_tokens_that_exist(cls):
        res = Client.imx_client.db.tokens()
        result = res["result"]
        return result

    @classmethod
    def get_token_balance_of_user(cls):
        res = Client.imx_client.db.balances(owner=Client._sender)
        result = res["result"]
        return result


    @classmethod
    def get_trade_with_buy_token_id_and_min_timestamp(cls, buy_token_id, min_timestamp_str):
        res = Client.imx_client.db.trades(party_b_token_id=buy_token_id, min_timestamp=min_timestamp_str)
        result = res["result"]
        return result


    @classmethod
    def cancel_order(cls, order_id):
        cancel_params = CancelOrderParams(order_id=order_id)
        future = Client.imx_client.cancel_order(cancel_params)
        res = future.result()
        print(res)

        Client.imx_client.db.stark_key()


    @classmethod
    def create_sell_order(cls, sell_card_token_id, currency_str, price_as_str):

        card_to_sell = ERC721(contract_addr="0xacb3c6a43d15b907e8433077b6d38ae40936fe2c", token_id=str(sell_card_token_id))

        currency_enum = Currency[currency_str]

        if currency_enum == Currency.GODS:
            buy_demand = ERC20(symbol="GODS", contract_addr="0xccc8cb5229b0ac8069c51fd58367fd1e622afd97", quantity=price_as_str)
        elif currency_enum == Currency.ETH:
            buy_demand = ETH(quantity=price_as_str)

        create_order_params = CreateOrderParams(sender=Client._sender, token_sell=card_to_sell, token_buy=buy_demand)

        future = Client.imx_client.create_order(create_order_params)

        res = future.result()

        success = res["status"] == "success"

        if not success:
            if "result" in res:
                if res["result"] == '[TYPESCRIPTWRAPPER]: Rated limited':
                    None
                elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4039 Errcode: ETIMEDOUT':
                    None
                elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4058 Errcode: ENOENT':
                    None
                elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4077 Errcode: ECONNRESET':
                    None
                elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4079 Errcode: ECONNABORTED':
                    None
                elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -3008 Errcode: ENOTFOUND':
                    None
                elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4092 Errcode: EACCES':
                    None
                else:
                    print(res)

        if success:
            time.sleep(3)

        return success


    @classmethod
    def purchase_card(cls, purchase_order_id):

        gp = Gods_Unchained_Poller()
        order = gp.get_order_by_order_id(purchase_order_id)

        current_status = order.status

        if current_status != "active":
            print(f"This card is no longer available but now it is {current_status}")

        else:
            price_as_str = Number_Converter.get_float_str_from_quantity_decimal(quantity=order.quantity, decimals=order.decimals)
            price_as_float = Number_Converter.get_float_from_quantity_decimal(quantity=order.quantity, decimals=order.decimals)

            currency_prices_dic = CoinMarketCap_Scrapper.get_now_currency_price()

            price_euro = price_as_float * currency_prices_dic[order.currency]

            print(f"Do you want to spend {price_euro:.3f} EUR or {price_as_float:.3f} {order.currency} to purchase \"{order.card_name}\"? Type yes to purchase.")

            answer = input()

            if answer == "yes":

                card_to_buy = ERC721(contract_addr="0xacb3c6a43d15b907e8433077b6d38ae40936fe2c", token_id=str(order.token_id))

                if order.currency == "GODS":
                    purchase_offer = ERC20(symbol="GODS", contract_addr="0xccc8cb5229b0ac8069c51fd58367fd1e622afd97", quantity=price_as_str)
                elif order.currency == "ETH":
                    purchase_offer = ETH(quantity=price_as_str)

                create_trade_params = CreateTradeParams(order_id=purchase_order_id, sender=Client._sender, token_sell=purchase_offer, token_buy=card_to_buy)
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


    #####


    @classmethod
    def _automatically_purchase_card(cls, purchase_order_id, sale_currency, classification_dic):

        additional_info_dic_1 = {}
        additional_info_dic_1["order_id"] = purchase_order_id
        order = Safe_Gods_Unchained_Poller.safe_download(task="get_order_by_order_id", information_dic=additional_info_dic_1)

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

                other_orders_list = Safe_Gods_Unchained_Poller.safe_download(task="get_all_active_sell_orders_for_a_currency_and_quality", information_dic=additional_info_dic_2)

            else:
                raise Exception("Implement how the orders were classified")

            currency_price_float_list = [Number_Converter.get_float_from_quantity_decimal(quantity=other_order.quantity, decimals=other_order.decimals) for other_order in other_orders_list]
            currency_price_float_list.sort()
            min_sale_price_currency_float = currency_price_float_list[0]

            current_currency_dic = CoinMarketCap_Scrapper.get_now_currency_price()
            min_sale_price_euro_float = current_currency_dic[sale_currency] * min_sale_price_currency_float
            purchase_price_euro_float = current_currency_dic[order.currency] * Number_Converter.get_float_from_quantity_decimal(quantity=order.quantity, decimals=order.decimals)


            if min_sale_price_euro_float >= (min_profit_span * purchase_price_euro_float):

                price_as_str = Number_Converter.get_float_str_from_quantity_decimal(quantity=order.quantity, decimals=order.decimals)

                card_to_buy = ERC721(contract_addr="0xacb3c6a43d15b907e8433077b6d38ae40936fe2c", token_id=str(order.token_id))

                if order.currency == "GODS":
                    purchase_offer = ERC20(symbol="GODS", contract_addr="0xccc8cb5229b0ac8069c51fd58367fd1e622afd97", quantity=price_as_str)
                elif order.currency == "ETH":
                    purchase_offer = ETH(quantity=price_as_str)

                create_trade_params = CreateTradeParams(order_id=purchase_order_id, sender=Client._sender, token_sell=purchase_offer, token_buy=card_to_buy)

                future = Client.imx_client.create_trade(create_trade_params)

                res = future.result()
                success = res["status"] == 'success'

                if success:
                    time.sleep(5)

                    additional_info_dic_3 = {}
                    additional_info_dic_3["order_id"] = purchase_order_id
                    new_order = Safe_Gods_Unchained_Poller.safe_download(task="get_order_by_order_id", information_dic=additional_info_dic_3)

                    if new_order.status == "filled":
                        return False, new_order, True

                    else:
                        print(f"Something went wrong with purchasing order {purchase_order_id}.")
                        print(json.dumps(new_order.to_print_dic(), indent=4))
                        return True, None, False

                else:
                    if "result" in res:
                        if res["result"] == '[TYPESCRIPTWRAPPER]: Rated limited':
                            None
                        elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4039 Errcode: ETIMEDOUT':
                            None
                        elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4058 Errcode: ENOENT':
                            None
                        elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4077 Errcode: ECONNRESET':
                            None
                        elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4079 Errcode: ECONNABORTED':
                            None
                        elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -3008 Errcode: ENOTFOUND':
                            None
                        elif res["result"] == '[TYPESCRIPTWRAPPER]: Errno: -4092 Errcode: EACCES':
                            None

                        else:
                            print(res)
                    else:
                        print(res)

                    print("The purchase did potentially not happen.")
                    return True, None, False

            else:
                print(f"The purchase of \"{order.card_name}\" is no longer profitable.")
                return True, None, True