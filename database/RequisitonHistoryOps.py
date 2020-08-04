import traceback
from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector

class RequisitionHistory:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__reqn = {}
        if self.__id != "":
            self.__cursor.execute("""select * from requisition_history where _id = %s""", (self.__id, ))
            self.__reqn = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_reqn(self, buyer_id, product_name, category, quantity, quantity_basis, product_description):
        self.__reqn['buyer_id'] = buyer_id
        self.__reqn['product_name'] = product_name
        self.__reqn['product_description'] = product_description
        self.__reqn['category'] = category
        self.__reqn['quantity'] = quantity
        self.__reqn['quantity_basis'] = quantity_basis
        self.__reqn['created_at'] = GenericOps.get_current_timestamp()
        self.__reqn['_id'] = self.insert(self.__reqn)
        return self.__reqn['_id']

    def insert(self, values, table="requisition_history_table"):
        try:
            self.__cursor.execute(Implementations.reqn_history_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO requisition_history (buyer_id, product_name, product_description, category, quantity, quantity_basis, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['buyer_id'], values['product_name'], values['product_description'],
                                   values['category'], values['quantity'], values['quantity_basis'],
                                   values['created_at']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='RequisitionHistoryOps', function_name='insert()')
            log.log(error, priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='RequisitionHistoryOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def get_reqn_id(self):
        return self.__reqn['_id']

    def get_product_name(self):
        return self.__reqn['product_name']

    def get_product_description(self):
        return self.__reqn['product_description']

    def get_category(self):
        return self.__reqn['category']

    def get_quantity(self):
        return self.__reqn['quantity']

    def get_quantity_basis(self):
        return self.__reqn['quantity_basis']

    def get_buyer_id(self):
        return self.__reqn['buyer_id']

    def get_created_at(self):
        return self.__reqn['created_at']
