import time
from src.operators.datacreator import DataCreator
from src.operators.helpers.file_helpers import FileMoverHelper


class ProcessingManager:
    """
    A class to handle the data processing process
    """

    def __init__(self):
        """
        The constructor to the ProcessingManager class
        """
        self._wait_until_restart = False
        self._keep_going = True
        self.observer = None

    def restart(self):
        """
        A method to restart the processing process
        :return: None
        """
        self._wait_until_restart = False

    def shutdown(self):
        """
        A method to shutdown the processing process
        :return:
        """
        self._keep_going = False

    def notify_observers(self, message, sender):
        """
        A method to notify observers of a message
        :param message: a message to be passed along
        :param sender: the sender of the process
        :return: None
        """
        self.observer.inform(message, sender)

    def processing_new_data(self, get_type, active_updated_orders_df):
        """
        A method to process new data
        :param get_type: the type of orders to be processed i.e. buy
        :param active_updated_orders_df: the current active updated orders DataFrame
        :return: None
        """

        dc = DataCreator()

        while self._keep_going:

            number_of_existing_files = FileMoverHelper.move_to_be_processed_files_for_processing(get_type)

            if number_of_existing_files > 0:
                new_active_updated_orders_df = dc.parallel_process_downloaded_info(get_type_string=get_type, active_updated_orders_df=active_updated_orders_df)
                active_updated_orders_df = new_active_updated_orders_df

            else:
                print(f"No new data has been downloaded")
                time.sleep(1)

        print("Shutdown processing_new_data")
