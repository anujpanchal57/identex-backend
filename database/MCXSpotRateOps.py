import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
from openpyxl.styles import Alignment, Font
import mysql.connector
from exceptions import exceptions


class MCXSpotRate:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__mcx_spot_rate = {}
        if self.__id != "":
            self.__cursor.execute("""select * from mcx_spot_rate where spot_id = %s""", (self.__id,))
            self.__mcx_spot_rate = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def get_all_spot_rates(self, status=True):
        try:
            self.__cursor.execute("""select * from mcx_spot_rate where status = %s""", (status, ))
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='MCXSpotRateOps', function_name='get_all_spot_rates()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to fetch spot rates, please try again")
        except Exception as e:
            log = Logger(module_name='MCXSpotRateOps', function_name='get_all_spot_rates()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to fetch spot rates, please try again")
