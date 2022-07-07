import sys
import traceback
from src.objects.orders.gods_unchained.orderadministratorgu import OrderAdministratorGU
from src.parallel_workers.parallelcardsupervisor import ParallelCardSupervisor


class TradingManager:
    """
    A class to supervise the inventory
    """

    def __init__(self):
        """
        The constructor of the TradingManager class
        """
        self._pcs = ParallelCardSupervisor()

    def supervise_inventory_list(self, start_inventory_list, start_balance):
        """
        A method to supervise the inventory
        :param start_inventory_list: the current inventory list
        :param start_balance: the start token balance
        :return: None
        """

        start_active_updated_orders_df = OrderAdministratorGU.create_active_updated_orders_df(get_type_string="SELL")

        try:
            self._pcs.keep_going = True
            self._pcs.parallel_supervise_inventory(start_inventory_list, start_active_updated_orders_df,
                                                         start_balance)

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
