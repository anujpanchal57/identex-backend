import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector

class Quotation:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__quotation = {}
        if self.__id != "":
            self.__cursor.execute("""select * from quotations where quotation_id = %s""", (self.__id, ))
            self.__quotation = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_quotation(self, supplier_id, requisition_id, remarks, quote_validity, delivery_time, total_amount,
                        total_gst, status=True):
        self.__quotation['supplier_id'] = supplier_id
        self.__quotation['requisition_id'] = requisition_id
        self.__quotation['remarks'] = remarks
        self.__quotation['quote_validity'] = GenericOps.convert_datestring_to_timestamp(quote_validity)
        self.__quotation['delivery_time'] = delivery_time
        self.__quotation['total_amount'] = total_amount
        self.__quotation['total_gst'] = total_gst
        self.__quotation['status'] = status
        self.__quotation['created_at'] = GenericOps.get_current_timestamp()
        self.__quotation['quotation_id'] = self.insert(self.__quotation)
        return self.__quotation['quotation_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.quotations_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO quotations (supplier_id, requisition_id, remarks, quote_validity, delivery_time, total_amount,
                        total_gst, status, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['supplier_id'], values['requisition_id'], values['remarks'], values['quote_validity'],
                                   values['delivery_time'], values['total_amount'], values['total_gst'],
                                   values['status'], values['created_at']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='QuotationOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='QuotationOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False
