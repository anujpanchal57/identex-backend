import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector

class Product:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__product = {}
        if self.__id != "":
            self.__cursor.execute("""select * from products where reqn_product_id = %s""", (self.__id, ))
            self.__product = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_product(self, product_id, lot_id, buyer_id, product_description, unit, quantity=0):
        self.__product['lot_id'] = lot_id
        self.__product['product_id'] = product_id
        self.__product['buyer_id'] = buyer_id
        self.__product['product_description'] = product_description
        self.__product['quantity'] = quantity
        self.__product['unit'] = unit
        return self.insert(self.__product)

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.products_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO products (product_id, lot_id, buyer_id, product_description, quantity, 
            unit) VALUES (%s, %s, %s, %s, %s, %s)""",
                                  (values['product_id'], values['lot_id'], values['buyer_id'],
                                   values['product_description'], values['quantity'], values['unit']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='ProductOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='ProductOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def insert_many(self, values):
        try:
            self.__cursor.execute(Implementations.products_create_table)
            # Inserting the record in the table
            self.__cursor.executemany("""INSERT INTO products (product_id, lot_id, buyer_id, product_description, quantity, 
            unit) VALUES (%s, %s, %s, %s, %s, %s)""", values)
            self.__sql.commit()
            last_row_id = self.__cursor.lastrowid
            result_ids = [last_row_id]
            for x in range(1, len(values)):
                result_ids.append(last_row_id + x)
            return result_ids

        except mysql.connector.Error as error:
            log = Logger(module_name='ProductOps', function_name='insert_many()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='ProductOps', function_name='insert_many()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def get_lot_products(self, lot_id):
        try:
            self.__cursor.execute("""select p.reqn_product_id, pm.product_id, pm.product_name, idc.category_name as product_category, 
                                    p.product_description, p.quantity, p.unit, idsc.sub_category_name as product_sub_category
                                    from products as p 
                                    join product_master as pm
                                    on p.product_id = pm.product_id
                                    join idntx_category as idc
                                    on pm.product_category = idc.category_id
                                    join idntx_sub_categories as idsc
                                    on pm.product_sub_category = idsc.sub_category_id
                                    where p.lot_id = %s;""", (lot_id, ))
            res = self.__cursor.fetchall()
            self.__sql.commit()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='ProductOps', function_name='get_lot_products()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='ProductOps', function_name='get_lot_products()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def get_product_details(self):
        try:
            self.__cursor.execute("""select pm.product_id, pm.product_name, idc.category_name
                                    from products as p 
                                    join product_master as pm
                                    on p.product_id = pm.product_id
                                    join idntx_category as idc
                                    on pm.product_category = idc.category_id
                                    where p.reqn_product_id = %s;""", (self.__id, ))
            res = self.__cursor.fetchone()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='ProductOps', function_name='get_product_details()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='ProductOps', function_name='get_product_details()')
            log.log(traceback.format_exc(), priority='highest')
            return False

# pprint(Product(1000).get_product_details())
# pprint(Product().get_lot_products(1000))
# pprint(Product("").add_product(1000, "filters", "steel", "filtering filters", "piece", 2))