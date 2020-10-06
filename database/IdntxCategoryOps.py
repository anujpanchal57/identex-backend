import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class IdntxCategory:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__idntx_category = {}
        if self.__id != "":
            self.__cursor.execute("""select * from idntx_category where category_id = %s""", (self.__id, ))
            self.__idntx_category = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def get_categories(self):
        self.__cursor.execute("""select * from idntx_category where status = true order by category_name""")
        res = self.__cursor.fetchall()
        if res is None:
            res = []
        return res
