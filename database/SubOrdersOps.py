import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class SubOrder:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__sub_order = {}
        if self.__id != "":
            self.__cursor.execute("""select * from sub_orders where order_id = %s""", (self.__id, ))
            self.__sub_order = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def insert_many(self, values):
        try:
            self.__cursor.execute(Implementations.sub_orders_create_table)
            # Inserting the record in the table
            self.__cursor.executemany("""INSERT INTO sub_orders (po_id, product_id, created_at, product_description, 
                                        gst, per_unit, amount, delivery_time, unit_currency) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", values)
            self.__sql.commit()
            last_row_id = self.__cursor.lastrowid
            result_ids = [last_row_id]
            for x in range(1, len(values)):
                result_ids.append(last_row_id + x)
            return result_ids

        except mysql.connector.Error as error:
            log = Logger(module_name='SubOrderOps', function_name='insert_many()')
            log.log(str(error), priority='critical')
            raise exceptions.IncompleteRequestException('Failed to order line items, please try again')
        except Exception as e:
            log = Logger(module_name='SubOrderOps', function_name='insert_many()')
            log.log(traceback.format_exc(), priority='critical')
            raise exceptions.IncompleteRequestException('Failed to add order line items, please try again')