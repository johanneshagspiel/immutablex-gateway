import json

from objects.inventory.inventory_entry import Inventory_Entry
from util.helpers import Safe_Datetime_Converter


class Inventory_Entry_Factory():

    def __init__(self):
        None

    @staticmethod
    def create_entry_from_text(line):
        json_line = json.loads(line)

        card_name = json_line["card_name"]
        token_id = json_line["token_id"]
        order_id = json_line["order_id"]

        purchase_price_currency = json_line["purchase_price_currency"]
        purchase_currency = json_line["purchase_currency"]
        purchase_price_euro = json_line["purchase_price_euro"]
        purchase_timestamp = Safe_Datetime_Converter.string_to_datetime(json_line["purchase_timestamp"])

        sale_currency = json_line["sale_currency"]
        sale_price_currency = json_line["sale_price_currency"]

        card_quality = json_line["card_quality"]

        new_inventory_entry = Inventory_Entry(card_name, token_id, order_id, purchase_price_currency, purchase_currency,
                                              purchase_price_euro, purchase_timestamp, sale_currency, sale_price_currency,
                                              card_quality)

        return new_inventory_entry