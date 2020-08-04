import traceback

import mysql.connector
from functionality import GenericOps, response
from functionality.Logger import Logger
from utility import DBConnectivity, conf, Implementations
from pprint import pprint

class Supplier:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__supplier = {}
        if self.__id != "":
            self.__cursor.execute("""select * from suppliers where _id = %s""", (self.__id, ))
            self.__supplier = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    # Adding a new supplier
    def add_supplier(self, company_name, activation_status=True, company_logo=""):
        self.__supplier['company_name'] = company_name
        self.__supplier['activation_status'] = activation_status
        self.__supplier['company_logo'] = company_logo
        timestamp = GenericOps.get_current_timestamp()
        self.__supplier['created_at'] = timestamp
        self.__supplier['updated_at'] = timestamp
        self.__supplier['_id'] = self.insert(self.__supplier)
        return self.__supplier['_id']

    def get_company_logo(self):
        return self.__supplier['company_logo']

    def get_company_name(self):
        return self.__supplier['company_name']

    def get_activation_status(self):
        return self.__supplier['activation_status']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.supplier_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO suppliers (company_name, company_logo, activation_status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)""",
                                  (values['company_name'], values['company_logo'], values['activation_status'],
                                   values['created_at'], values['updated_at']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierOps', function_name='insert()')
            log.log(error, priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='SupplierOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

# pprint(Supplier(1000))
# pprint(Supplier("").add_supplier("Bhavani"))
