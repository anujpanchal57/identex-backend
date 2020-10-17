import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class PO:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__po = {}
        if self.__id != "":
            self.__cursor.execute("""select * from purchase_orders where po_id = %s""", (self.__id, ))
            self.__po = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_po(self, po_no, buyer_id, supplier_id, acquisition_id, acquisition_type, total_amount, total_gst, notes='', tnc=''):
        self.__po['po_no'], self.__po['buyer_id'], self.__po['supplier_id'] = po_no, buyer_id, supplier_id
        self.__po['total_amount'], self.__po['total_gst'] = total_amount, total_gst
        self.__po['notes'], self.__po['tnc'] = notes, tnc
        self.__po['acquisition_id'], self.__po['acquisition_type'] = acquisition_id, acquisition_type
        self.__po['po_id'] = self.insert(self.__po)
        return self.__po['po_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.po_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO purchase_orders (po_no, buyer_id, supplier_id, acquisition_id, acquisition_type, 
                                        total_amount, total_gst, notes, tnc) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['po_no'], values['buyer_id'], values['supplier_id'],
                                   values['acquisition_id'], values['acquisition_type'],
                                   values['total_amount'], values['total_gst'], values['notes'], values['tnc']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='PurchaseOrderOps', function_name='insert()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add purchase order, please try again')
        except Exception as e:
            log = Logger(module_name='PurchaseOrderOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add purchase order, please try again')

    def set_po_no(self, po_no):
        try:
            self.__po['po_no'] = po_no
            self.__cursor.execute("""update purchase_orders set po_no = %s where po_id = %s""", (po_no, self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='PurchaseOrderOps', function_name='set_po_no()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update PO number, please try again")
        except Exception as e:
            log = Logger(module_name='PurchaseOrderOps', function_name='set_po_no()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update PO number, please try again")