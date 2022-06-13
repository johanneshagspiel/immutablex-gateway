import time
import traceback
from operators.data_creator import Data_Creator
from operators.helpers.file_helpers import File_Mover_Helper


class Processing_Manager():

    def __init__(self):
        self._wait_until_restart = False
        self._keep_going = True
        self.observer = None


    def restart(self):
        self._wait_until_restart = False

    def shutdown(self):
        self._keep_going = False

    def notify_observers(self, message, sender):
        self.observer.inform(message, sender)


    def processing_new_data(self, get_type, active_updated_orders_df):

        dc = Data_Creator()

        while self._keep_going:

            number_of_existing_files = File_Mover_Helper.move_to_be_processed_files_for_processing(get_type)

            if number_of_existing_files > 0:
                new_active_updated_orders_df = dc.parallel_process_downloaded_info(get_type_string=get_type, active_updated_orders_df=active_updated_orders_df)
                active_updated_orders_df = new_active_updated_orders_df

            else:
                print(f"No new data has been downloaded")
                time.sleep(1)

        print("Shutdown processing_new_data")
