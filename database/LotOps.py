import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class Lot:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__lot = {}
        if self.__id != "":
            self.__cursor.execute("""select * from lots where lot_id = %s""", (self.__id, ))
            self.__lot = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_lot(self, requisition_id, lot_name, lot_description, lot_category, lot_sub_category, force_lot_bidding=True):
        self.__lot['requisition_id'] = requisition_id
        self.__lot['lot_name'] = lot_name
        self.__lot['lot_description'] = lot_description
        self.__lot['force_lot_bidding'] = force_lot_bidding
        self.__lot['created_at'] = GenericOps.get_current_timestamp()
        self.__lot['lot_category'], self.__lot['lot_sub_category'] = lot_category, lot_sub_category
        self.__lot['lot_id'] = self.insert(self.__lot)
        return self.__lot['lot_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.lots_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO lots (requisition_id, lot_name, lot_description, force_lot_bidding, created_at, lot_category, lot_sub_category) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                  (values['requisition_id'], values['lot_name'],
                                   values['lot_description'], values['force_lot_bidding'], values['created_at'],
                                   values['lot_category'], values['lot_sub_category']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='LotOps', function_name='insert()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add lot details, please try again')
        except Exception as e:
            log = Logger(module_name='LotOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add lot details, please try again')

    def get_lot_for_requisition(self, requisition_id):
        self.__cursor.execute("""select * from lots where requisition_id = %s""", (requisition_id, ))
        self.__lot = self.__cursor.fetchone()
        self.__sql.commit()
        return self.__lot

# pprint(Lot().add_lot(1000, "sample", "sample"))
# pprint(Lot().get_lot_for_requisition(1000))