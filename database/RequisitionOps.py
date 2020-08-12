import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector

class Requisition:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__requisition = {}
        if self.__id != "":
            self.__cursor.execute("""select * from requisitions where requisition_id = %s""", (self.__id, ))
            self.__requisition = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_requisition(self, requisition_name, buyer_id, timezone, currency, deadline, tnc="", cancelled=False, status=True, supplier_instructions=""):
        self.__requisition['requisition_name'] = requisition_name
        self.__requisition['buyer_id'] = buyer_id
        self.__requisition['timezone'] = timezone
        self.__requisition['deadline'] = deadline
        self.__requisition['currency'] = currency
        self.__requisition['supplier_instructions'] = supplier_instructions
        self.__requisition['tnc'] = tnc
        self.__requisition['cancelled'] = cancelled
        self.__requisition['status'] = status
        self.__requisition['created_at'] = GenericOps.get_current_timestamp()
        self.__requisition['requisition_id'] = self.insert(self.__requisition)
        return self.__requisition['requisition_id']

    def insert(self, values, table="requisition_table"):
        try:
            self.__cursor.execute(Implementations.requisition_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO requisitions (buyer_id, requisition_name, timezone, currency, deadline, supplier_instructions, 
            tnc, cancelled, status, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['buyer_id'], values['requisition_name'], values['timezone'], values['currency'],
                                   values['deadline'], values['supplier_instructions'], values['tnc'],
                                   values['cancelled'], values['status'], values['created_at']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='RequisitionOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='RequisitionOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def get_rfq(self, buyer_id):
        try:
            self.__cursor.execute("""select * from requisitions as r join lots as l on r.requisition_id = l.requisition_id and r.buyer_id = %s;""", (buyer_id, ))
            res = self.__cursor.fetchall()
            self.__sql.commit()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='RequisitionOps', function_name='get_rfq()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='RequisitionOps', function_name='get_rfq()')
            log.log(traceback.format_exc(), priority='highest')
            return False

# pprint(Requisition().get_rfq(1000))