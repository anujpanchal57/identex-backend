import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class Pincode:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def search_by_pincode(self, pincode, offset=0, limit=10):
        self.__cursor.execute("select * from pincodes where pincode like '" + pincode + "%' limit " + str(offset) + ", " + str(limit))
        res = self.__cursor.fetchall()
        return res

# pprint(Pincode().search_by_pincode("400078"))