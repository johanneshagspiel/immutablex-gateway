import json

from src.objects.inventory.inventory_entry import InventoryEntry
from src.util.helpers import SafeDatetimeConverter


class InventoryEntryFactory:
    """
    A factory class to create one InventoryEntry instance.
    """

    def __init__(self):
        """
        The constructor of the InventoryEntryFactory class.
        """
        pass

    @staticmethod
    def create_entry_from_text(line):
        """
        Method to convert one line of text into an InventoryEntry
        :param line: the InventoryEntry as a string
        :return: one instance of InventoryEntry
        """
        json_line = json.loads(line)

        card_name = json_line["card_name"]
        token_id = json_line["token_id"]
        order_id = json_line["order_id"]

        purchase_price_currency = json_line["purchase_price_currency"]
        purchase_currency = json_line["purchase_currency"]
        purchase_price_euro = json_line["purchase_price_euro"]
        purchase_timestamp = SafeDatetimeConverter.string_to_datetime(json_line["purchase_timestamp"])

        sale_currency = json_line["sale_currency"]
        sale_price_currency = json_line["sale_price_currency"]

        card_quality = json_line["card_quality"]

        new_inventory_entry = InventoryEntry(card_name, token_id, order_id, purchase_price_currency, purchase_currency,
                                             purchase_price_euro, purchase_timestamp, sale_currency,
                                             sale_price_currency, card_quality)

        return new_inventory_entry
