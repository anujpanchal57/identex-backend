import traceback

import mysql.connector
from functionality import GenericOps, response
from functionality.Logger import Logger
from utility import DBConnectivity, conf, Implementations
from pprint import pprint
from exceptions import exceptions

class SupplierGSTDetails:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__gst_details = {}
        if self.__id != "":
            self.__cursor.execute("""select * from supplier_gst_details where gst_details_id = %s""", (self.__id, ))
            self.__gst_details = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_gst_details(self, supplier_id, gst_no, filing_frequency, status):
        self.__gst_details['supplier_id'], self.__gst_details['gst_no'] = supplier_id, gst_no
        self.__gst_details['filing_frequency'], self.__gst_details['status'] = filing_frequency, status
        self.__gst_details['gst_details_id'] = self.insert(self.__gst_details)
        return self.__gst_details['gst_details_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.supplier_gst_details_create_table)
            # Checking whether the record is added or not
            self.__cursor.execute("""select * from supplier_gst_details where supplier_id = %s""",
                                  (values['supplier_id'],))
            gst = self.__cursor.fetchall()
            if gst is None:
                is_gst_added = False
            else:
                is_gst_added = True if len(gst) > 0 else False
            # If GST is present, then return True
            if is_gst_added:
                return True
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO supplier_gst_details (supplier_id, gst_no, filing_frequency, status) 
                                    VALUES (%s, %s, %s, %s)""",
                                  (values['supplier_id'], values['gst_no'], values['filing_frequency'],
                                   values['status']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierGSTDetailsOps', function_name='insert()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add gst details, please try again')
        except Exception as e:
            log = Logger(module_name='SupplierGSTDetailsOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add gst details, please try again')

    def get_gst_details(self, supplier_id):
        try:
            self.__cursor.execute("""select gst_no, filing_frequency, status from supplier_gst_details where supplier_id = %s""", (supplier_id, ))
            res = self.__cursor.fetchall()
            if len(res) == 0:
                res = {}
                return res
            res = res[0]
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierGSTDetailsOps', function_name='get_gst_details()')
            log.log(str(error), priority='highest')
            return {}
        except Exception as e:
            log = Logger(module_name='SupplierGSTDetailsOps', function_name='get_gst_details()')
            log.log(traceback.format_exc(), priority='highest')
            return {}