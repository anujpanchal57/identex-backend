from functionality import GenericOps
from utility import DBConnectivity, conf
from pprint import pprint

class RFQ:
    def __init__(self, _id=""):
        self.__id = _id
        self.__mongo = DBConnectivity.create_sql_connection()
        self.__rfq = {}
        if self.__id != "":
            self.__rfq = self.__mongo[conf.mongoconfig.get('tables').get("rfq_table")].find_one({"_id": self.__id})

    def create_rfq(self):
        pass

