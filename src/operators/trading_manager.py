import sys
import traceback

from objects.orders.gods_unchained.order_administrator_gu import Order_Administrator_GU
from parallel_workers.parallel_card_supervisor import Parallel_Card_Supervisor


class Trading_Manager():


    def __init__(self):
        self._pcs = Parallel_Card_Supervisor()


    def supervise_inventory_list(self, start_inventory_list, start_balance):

        start_active_updated_orders_df = Order_Administrator_GU.create_active_updated_orders_df(get_type_string="SELL")

        try:
            self._pcs.keep_going = True
            self._pcs.parallel_download_timestamp_orders(start_inventory_list, start_active_updated_orders_df, start_balance)

        except KeyboardInterrupt:
            print("Shutting down trading")
            self._pcs.keep_going = False
            sys.exit()

        except Exception as e:
            print(type(e))
            print(e)
            self._pcs.keep_going = False
            traceback.print_exc()
            sys.exit()
