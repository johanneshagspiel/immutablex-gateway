import json
import traceback

import mysql.connector

from src.util.files.filehandler import FileHandler


class MysqlConnector:

    def __init__(self):

        mysql_info_file_path = FileHandler.get_base_path("mysql_info_file")
        with open(mysql_info_file_path, 'r', encoding='utf-8') as mysql_info_file:
            mysql_info_dic = json.load(mysql_info_file)
        mysql_info_file.close()

        self.db = mysql_info_dic["db"]
        if len(self.db) == 0:
            raise Exception("No name of the MYSQL database was found - add it to resources/client_info/mysql_info.json")

        self.user = mysql_info_dic["user"]
        if len(self.user) == 0:
            raise Exception("No user name for the MYSQL connection was found - add it to resources/client_info/mysql_info.json")

        self.password = mysql_info_dic["password"]
        if len(self.password) == 0:
            raise Exception("No password for the MYSQL connection was found - add it to resources/client_info/mysql_info.json")

        self.host = mysql_info_dic["host"]
        if len(self.host) == 0:
            raise Exception("No host address for the MYSQL connection was found - add it to resources/client_info/mysql_info.json")

        self.port = mysql_info_dic["port"]
        if len(self.port) == 0:
            raise Exception("No port for the MYSQL connection was found - add it to resources/client_info/mysql_info.json")


    def insert_list_of_gu_orders(self, order_list, mode):

        try:
            conn = mysql.connector.connect(database=self.db,
                                           user=self.user,
                                           password=self.password,
                                           host=self.host,
                                           port=int(self.port))


            cursor = conn.cursor()

            tuple_list = [x.to_tuple() for x in order_list]

            if mode == "gu_orders":
                # prepared_statement = """INSERT INTO gu_orders (order_id, user, token_id, token_address, status, type,
                # card_name, card_quality, quantity, decimals, currency, price_euro, timestamp, updated_timestamp ) VALUES
                # (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

                cursor.executemany("""INSERT INTO gu_orders (order_id, user, token_id, token_address, status, type, 
                    card_name, card_quality, quantity, decimals, currency, price_euro, timestamp, updated_timestamp ) VALUES 
                    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", tuple_list)


            elif mode == "to_be_processed_gu_orders":
                # prepared_statement = """INSERT INTO to_be_processed_gu_orders (order_id, user, token_id, token_address, status, type,
                # card_name, card_quality, quantity, decimals, currency, price_euro, timestamp, updated_timestamp ) VALUES
                # (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

                cursor.executemany("""INSERT INTO to_be_processed_gu_orders (order_id, user, token_id, token_address, status, type, 
                    card_name, card_quality, quantity, decimals, currency, price_euro, timestamp, updated_timestamp ) VALUES 
                    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", tuple_list)


            # for index, order in enumerate(order_list):
            #     order_tuple = order.to_tuple()
            #     cursor.execute(prepared_statement, order_tuple)
            #     print(str(index) + "/" + str(len(order_list)))


            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            traceback.print_exc()
            print(e)
            raise e
