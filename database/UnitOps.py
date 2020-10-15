import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint

class Unit:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__unit = {}

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def get_all_units(self):
        self.__cursor.execute("""select distinct(unit_name) from units order by unit_name""")
        res = self.__cursor.fetchall()
        if res is None:
            result = []
        result = [x['unit_name'] for x in res]
        return result
