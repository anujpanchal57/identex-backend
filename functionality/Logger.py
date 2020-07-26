import uuid

import requests

from functionality import DictionaryOps
from functionality import GenericOps
from utility import DBConnectivity
from utility import conf


class Logger:

    def __init__(self,module_name,function_name):
        self.__module_name = module_name
        self.__function_name = function_name
        self.__log_id = str(uuid.uuid4())
        self.__mongo = DBConnectivity.create_mongo_connection()
        self.__log = DictionaryOps.convert_mongo_cursor_to_dict(self.__mongo[conf.mongoconfig.get('tables').get('log_table')].find({}))

    def log(self,error,priority='high'):
        log = {'log_id': self.__log_id, 'message':error, 'priority': priority, 'module_name' : self.__module_name, 'function_name': self.__function_name,'timestamp':GenericOps.get_current_timestamp()}
        self.__mongo[conf.mongoconfig.get('tables').get('log_table')].update({'_id': self.__log_id}, {"$set": log}, upsert=True)
        return True