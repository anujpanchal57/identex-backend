import traceback
from pprint import pprint

import jwt
import mysql.connector
from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from exceptions import exceptions
from database.AuthorizationOps import Authorization

class Order:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__order = {}
        if self.__id != "":
            self.__cursor.execute("""select * from orders where order_id = %s""", (self.__id,))
            self.__order = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_order(self, buyer_id, supplier_id, quote_id, reqn_product_id, acquisition_id=0, acquisition_type="", po_no=""):
        self.__order['buyer_id'] = buyer_id
        self.__order['supplier_id'] = supplier_id
        self.__order['quote_id'] = quote_id
        self.__order['reqn_product_id'] = reqn_product_id
        self.__order['acquisition_id'] = acquisition_id
        self.__order['acquisition_type'] = acquisition_type
        self.__order['po_no'] = po_no
        self.__order['order_id']  =self.insert(self.__order)
        return self.__order['order_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.orders_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO orders (buyer_id, supplier_id, po_no, acquisition_id, acquisition_type, 
                                    quote_id, reqn_product_id) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                  (values['buyer_id'], values['supplier_id'], values['po_no'],
                                   values['acquisition_id'], values['acquisition_type'], values['quote_id'],
                                   values['reqn_product_id']))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to add order, please try again")
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to add order, please try again")


