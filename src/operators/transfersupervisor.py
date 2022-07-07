from datetime import datetime
from pandas import DataFrame
import numpy as np
from src.operators.helpers.competitionhandler import CompetitionHandler
from src.operators.client import Client
from src.scrappers.godsunchainedpoller import GodsUnchainedPoller
from src.util.numberconverter import NumberConverter


class TransferSupervisor:
    """
    A class to supervise trades
    """

    def __init__(self):
        """
        The constructor of the TransferSupervisor
        """
        self._gp = GodsUnchainedPoller()

    def supervise_card(self, inventory_entry, all_cards_available, currency_prices_dic, competition_price_dic):
        """
        A method to supervise one card meaning to keep its price as low as possible above a certain threshold
        :param inventory_entry: the inventory entry associated with a card
        :param all_cards_available: all the cards also offered by the competitors
        :param currency_prices_dic: the current cryptocurrency prices
        :param competition_price_dic: the expected prices of the competitors
        :return: None
        """

        msg_card_name = inventory_entry.card_name
        msg_token_id = inventory_entry.token_id
        msg_list = [msg_card_name, msg_token_id]

        fee_to_pay = 1.01

        # base_price_floor_multiplier = 1.025
        # utc_time_now = datetime.utcnow()
        # purchase_time_utc = inventory_entry.purchase_timestamp
        # seconds_since_purchase = (utc_time_now - purchase_time_utc).total_seconds()
        # days_since_purchase = int(seconds_since_purchase / 86400)
        # price_floor_decay = days_since_purchase * 0.0025
        # price_floor_multiplier = 1 if (base_price_floor_multiplier - price_floor_decay <= 1) else base_price_floor_multiplier - price_floor_decay
        price_floor_multiplier = 1

        price_floor_crypto_str = NumberConverter.quantize_number_str((price_floor_multiplier * inventory_entry.purchase_price_euro) / currency_prices_dic[inventory_entry.sale_currency])
        price_floor_crypto_float = float(price_floor_crypto_str)
        price_floor_crypto_euro_float = currency_prices_dic[inventory_entry.sale_currency] * price_floor_crypto_float

        no_other_offers_price_str = NumberConverter.quantize_number_str((1.25 * inventory_entry.purchase_price_euro) / currency_prices_dic[inventory_entry.sale_currency])
        no_other_offers_price_float = float(no_other_offers_price_str)
        no_other_offers_price_euro_float = currency_prices_dic[inventory_entry.sale_currency] * no_other_offers_price_float

        if isinstance(all_cards_available, DataFrame):
            token_id_list = all_cards_available["token_id"].to_list()
            price_crypto_float_list = np.vectorize(lambda x, y: 1.05 * NumberConverter.get_float_from_quantity_decimal(x, y))(all_cards_available["quantity"], all_cards_available["decimals"])
            order_id_list = all_cards_available["order_id"].to_list()
            all_cards_available_list = list(zip(token_id_list, price_crypto_float_list, order_id_list))

        elif isinstance(all_cards_available, list):
            all_cards_available_list = [(x["sell"]["data"]["token_id"], NumberConverter.get_float_from_quantity_decimal(x["buy"]["data"]["quantity"], x["buy"]["data"]["decimals"]), x["order_id"]) for x in all_cards_available]

        token_id_list = [entry[0] for entry in all_cards_available_list]
        if inventory_entry.token_id in token_id_list:
            already_listed = True
            my_card_index = token_id_list.index(inventory_entry.token_id)

            current_entry = all_cards_available_list.pop(my_card_index)

            current_price_str = str(NumberConverter.quantize_number_str(current_entry[1]))
            current_price_float = float(current_price_str)
        else:
            already_listed = False

        missing_active_orders_list = []
        found_active_orders_list = []

        for token_id, base_price, order_id in all_cards_available_list:
            token_id_str = str(token_id)
            if token_id_str in competition_price_dic:
                entry = competition_price_dic[token_id_str]
                expected_base_price = entry[0]
                combined_price = entry[1]

                if expected_base_price == base_price:
                    found_active_orders_list.append((token_id_str, combined_price))
                else:
                    missing_active_orders_list.append(order_id)

            else:
                missing_active_orders_list.append(order_id)

        if len(missing_active_orders_list) > 0:

            competition_price_dic, additional_info_list = CompetitionHandler.add_missing_orders_to_competition_file(missing_active_orders_list, competition_price_dic, inventory_entry)

            # not_yet_passed = True
            # while not_yet_passed:
            #     try:
            #         competition_price_dic, additional_info_list = CompetitionHandler.add_missing_orders_to_competition_file(missing_active_orders_list, competition_price_dic, inventory_entry)
            #         not_yet_passed = False
            #     except RuntimeError as e:
            #         None

            correct_price_list = found_active_orders_list
            correct_price_list.extend(additional_info_list)

        else:
            correct_price_list = found_active_orders_list

        msg_list.append(competition_price_dic)

        sorted_other_offers = sorted(correct_price_list, key=lambda x: x[1])
        sorted_other_offers_adjusted = [(token_id, combined_price / fee_to_pay) for (token_id, combined_price) in sorted_other_offers]

        cheapest_offer_others_cur_float = sorted_other_offers_adjusted[0][1]
        cheapest_offer_others_eur_float = currency_prices_dic[inventory_entry.sale_currency] * cheapest_offer_others_cur_float

        if len(sorted_other_offers_adjusted) > 0:

            for price_position, (token_id, price_float) in enumerate(sorted_other_offers_adjusted):

                if price_float > price_floor_crypto_float:

                    price_str = NumberConverter.quantize_number_str(price_float)
                    next_cheapest_price_str = NumberConverter.get_next_cheapest_number(price_str)
                    next_cheapest_price_float = float(next_cheapest_price_str)
                    next_cheapest_price_euro_float = currency_prices_dic[inventory_entry.sale_currency] * next_cheapest_price_float

                    msg_time = datetime.utcnow()
                    if already_listed and next_cheapest_price_float == current_price_float:
                        msg_instruction = "slow"
                        msg_text = f"{price_position + 1}: Price can not be improved at {next_cheapest_price_euro_float:.3f}/{price_floor_crypto_euro_float:.3f}/{inventory_entry.purchase_price_euro:.3f} EUR or {(next_cheapest_price_float * 1.01):.10f} {inventory_entry.sale_currency} - {(cheapest_offer_others_cur_float * 1.01):.10f}/{cheapest_offer_others_eur_float:.3f} {inventory_entry.sale_currency}/EUR"

                    else:
                        success = Client.create_sell_order(inventory_entry.token_id, inventory_entry.sale_currency, next_cheapest_price_str)

                        if success:
                            msg_instruction = "fast"
                            msg_text = f"{price_position + 1}: Card offered at {next_cheapest_price_euro_float:.3f}/{price_floor_crypto_euro_float:.3f}/{inventory_entry.purchase_price_euro:.3f} EUR or {(next_cheapest_price_float * 1.01):.10f} {inventory_entry.sale_currency} to undercut {(price_float * 1.01):.10f} - {(cheapest_offer_others_cur_float * 1.01):.10f}/{cheapest_offer_others_eur_float:.3f} {inventory_entry.sale_currency}/EUR"
                        else:
                            msg_instruction = "fast"
                            msg_text = f"{price_position + 1}: Something went wrong offering this card at a new price"

                    msg_list.extend([msg_time, msg_instruction, msg_text])
                    return msg_list

            msg_time = datetime.utcnow()
            if current_price_float == price_floor_crypto_float:
                msg_instruction = "slow"
                msg_text = f"{len(sorted_other_offers_adjusted) + 1}: Price can not be improved at the price floor of {price_floor_crypto_euro_float:.3f}/{price_floor_crypto_euro_float:.3f}/{inventory_entry.purchase_price_euro:.3f} EUR or {(price_floor_crypto_float * 1.01):.10f} {inventory_entry.sale_currency} - {(cheapest_offer_others_cur_float * 1.01):.10f}/{cheapest_offer_others_eur_float:.3f} {inventory_entry.sale_currency}/EUR"

            else:
                success = Client.create_sell_order(inventory_entry.token_id, inventory_entry.sale_currency, price_floor_crypto_str)

                if success:
                    msg_instruction = "fast"
                    msg_text = f"{len(sorted_other_offers_adjusted) + 1}: Card offered at the price floor of {price_floor_crypto_euro_float:.3f}/{price_floor_crypto_euro_float:.3f}/{inventory_entry.purchase_price_euro:.3f} EUR or {(price_floor_crypto_float * 1.01):.10f} {inventory_entry.sale_currency} - {(cheapest_offer_others_cur_float * 1.01):.10f}/{cheapest_offer_others_eur_float:.3f} {inventory_entry.sale_currency}/EUR"
                else:
                    msg_instruction = "fast"
                    msg_text = "Something went wrong offering this card at the price floor"

            msg_list.extend([msg_time, msg_instruction, msg_text])
            return msg_list

        else:
            msg_time = datetime.utcnow()

            if current_price_float == no_other_offers_price_float:
                msg_instruction = "slow"
                msg_text = f"1: Card already is offered at {no_other_offers_price_euro_float:.3f}/{inventory_entry.purchase_price_euro:.3f} EUR or {(no_other_offers_price_float * 1.01):.10f} {inventory_entry.sale_currency} as there is no other offer"

            else:
                success = Client.create_sell_order(inventory_entry.token_id, inventory_entry.sale_currency, no_other_offers_price_str)

                if success:
                    msg_instruction = "fast"
                    msg_text = f"1: Card is offered at {no_other_offers_price_euro_float:.3f}/{inventory_entry.purchase_price_euro:.3f} EUR or {(no_other_offers_price_float * 1.01):.10f} {inventory_entry.sale_currency} as there is no other offer"
                else:
                    msg_instruction = "fast"
                    msg_text = "Something went wrong offering this card at the set price when there is no other offer"
            msg_list.extend([msg_time, msg_instruction, msg_text])
            return msg_list
