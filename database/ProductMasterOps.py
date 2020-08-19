import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector

class ProductMaster:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__product_master = {}
        if self.__id != "":
            self.__cursor.execute("""select * from product_master where product_id = %s""", (self.__id, ))
            self.__product_master = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_product(self, buyer_id, product_name, product_category):
        self.__product_master['buyer_id'] = buyer_id
        self.__product_master['product_name'] = product_name
        self.__product_master['product_category'] = product_category
        self.__product_master['created_at'] = GenericOps.get_current_timestamp()
        return self.insert(self.__product_master)

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.product_master_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO product_master (buyer_id, product_name, product_category, created_at) 
                                    VALUES (%s, %s, %s, %s)""",
                                  (values['buyer_id'], values['product_name'], values['product_category'],
                                   values['created_at']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='ProductMasterOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='ProductMasterOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def insert_many(self, values):
        try:
            self.__cursor.execute(Implementations.products_create_table)
            # Inserting the record in the table
            self.__cursor.executemany("""INSERT INTO product_master (buyer_id, product_name, product_category, created_at) 
                                    VALUES (%s, %s, %s, %s)""", values)
            self.__sql.commit()
            last_row_id = self.__cursor.lastrowid
            result_ids = [last_row_id]
            for x in range(1, len(values)):
                result_ids.append(last_row_id + x)
            return result_ids

        except mysql.connector.Error as error:
            log = Logger(module_name='ProductMasterOps', function_name='insert_many()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='ProductMasterOps', function_name='insert_many()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def is_product_added(self, product_name, product_category, buyer_id):
        try:
            self.__cursor.execute("""select * from product_master where lower(product_name) = %s and lower(product_category) = %s 
                                    and buyer_id = %s""",
                                  (product_name, product_category, buyer_id))
            res = self.__cursor.fetchone()
            self.__sql.commit()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='ProductMasterOps', function_name='is_product_added()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='ProductMasterOps', function_name='is_product_added()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def get_buyer_products(self, buyer_id):
        try:
            self.__cursor.execute("""select product_id, product_name, product_category, created_at 
                        from product_master where buyer_id = %s""", (buyer_id,))
            res = self.__cursor.fetchall()
            self.__sql.commit()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='ProductMasterOps', function_name='get_buyer_products()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='ProductMasterOps', function_name='get_buyer_products()')
            log.log(traceback.format_exc(), priority='highest')
            return False

# pprint(Product().get_lot_products(1000))
# pprint(Product("").add_product(1000, "filters", "steel", "filtering filters", "piece", 2))