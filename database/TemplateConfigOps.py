import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class TemplateConfig:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__temp_config = {}
        if self.__id != "":
            self.__cursor.execute("""select * from template_configs where template_id = %s""", (self.__id, ))
            self.__temp_config = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def get_template_config(self, buyer_id, template_type="purchase_order"):
        try:
            self.__cursor.execute("""select template_id, template_type, template_name, template_config
                                    from template_configs where buyer_id = %s and template_type = %s
                                    order by updated_at desc limit 1""",
                                  (buyer_id, template_type))
            res = self.__cursor.fetchone()
            if res is None:
                return []
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='TemplateConfigOps', function_name='get_template_config()')
            log.log(str(error), priority='critical')
            return []
        except Exception as e:
            log = Logger(module_name='TemplateConfigOps', function_name='get_template_config()')
            log.log(traceback.format_exc(), priority='critical')
            return []