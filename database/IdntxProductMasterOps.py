import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class IdntxProductMaster:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__idntx_product = {}
        if self.__id != "":
            self.__cursor.execute("""select * from idntx_products where product_id = %s""", (self.__id, ))
            self.__idntx_product = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def search_products(self, product_str, category_id, sub_category_id, start_limit=0, end_limit=10):
        self.__cursor.execute("select * from idntx_products where lower(product_name) like '%" + product_str + "%' and category_id = "+
                              str(category_id) + " and sub_category_id = " + str(sub_category_id) + " order by product_name limit " +
                              str(start_limit) + ", " + str(end_limit))
        res = self.__cursor.fetchall()
        if res is None:
            res = []
        return res

