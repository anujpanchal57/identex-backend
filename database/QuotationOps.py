import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

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

    def add_quotation(self, supplier_id, requisition_id, total_amount, total_gst, quote_validity, status=True):
        self.__quotation['supplier_id'] = supplier_id
        self.__quotation['requisition_id'] = requisition_id
        self.__quotation['total_amount'] = total_amount
        self.__quotation['quote_validity'] = GenericOps.convert_datestring_to_timestamp(quote_validity)
        self.__quotation['total_gst'] = total_gst
        self.__quotation['status'] = status
        self.__quotation['created_at'] = GenericOps.get_current_timestamp()
        self.__quotation['quotation_id'] = self.insert(self.__quotation)
        return self.__quotation['quotation_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.quotations_create_table)
            # update the status of previous quote to false if any
            self.__cursor.execute("""update quotations set status = false where requisition_id = %s and supplier_id = %s and status = true;""",
                                  (values['requisition_id'], values['supplier_id']))
            self.__sql.commit()
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO quotations (supplier_id, requisition_id, total_amount,
                        total_gst, quote_validity, status, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                  (values['supplier_id'], values['requisition_id'],
                                   values['total_amount'], values['total_gst'], values['quote_validity'],
                                   values['status'], values['created_at']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='QuotationOps', function_name='insert()')
            log.log(str(error), priority='critical')
            raise exceptions.IncompleteRequestException("Failed to add quotation, please try again")
        except Exception as e:
            log = Logger(module_name='QuotationOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='critical')
            raise exceptions.IncompleteRequestException("Failed to add quotation, please try again")

    def get_quotations_count_for_requisition(self, requisition_id, table="quotation_table"):
        try:
            self.__cursor.execute("""SELECT * FROM information_schema.tables WHERE table_schema = %s AND table_name = %s LIMIT 1;""",
                                  (conf.sqlconfig.get('database_name'), conf.sqlconfig.get('tables').get(table)))
            if self.__cursor.fetchone() is None:
                return 0
            self.__cursor.execute("""select count(*) as quotation_count
                                    from quotations
                                    where requisition_id = %s and status = True;""", (requisition_id, ))
            res = self.__cursor.fetchall()
            return res[0]['quotation_count']

        except mysql.connector.Error as error:
            log = Logger(module_name='QuotationOps', function_name='get_quotations_count_for_requisition()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='QuotationOps', function_name='get_quotations_count_for_requisition()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def get__supplier_quotations_count_for_requisition(self, requisition_id, supplier_id, table="quotation_table"):
        try:
            self.__cursor.execute("""SELECT * FROM information_schema.tables WHERE table_schema = %s AND table_name = %s LIMIT 1;""",
                                  (conf.sqlconfig.get('database_name'), conf.sqlconfig.get('tables').get(table)))
            if self.__cursor.fetchone() is None:
                return 0
            self.__cursor.execute("""select count(*) as quotation_count
                                    from quotations
                                    where requisition_id = %s and supplier_id = %s;""", (requisition_id, supplier_id))
            res = self.__cursor.fetchall()
            return res[0]['quotation_count']

        except mysql.connector.Error as error:
            log = Logger(module_name='QuotationOps', function_name='get__supplier_quotations_count_for_requisition()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='QuotationOps', function_name='get__supplier_quotations_count_for_requisition()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def remove_quotation(self, quotation_id):
        try:
            self.__cursor.execute("""delete from quotations where quotation_id = %s""", (quotation_id, ))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='QuotationOps', function_name='remove_quotation()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException("Failed to remove quotation, please try again")
        except Exception as e:
            log = Logger(module_name='QuotationOps', function_name='remove_quotation()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException("Failed to remove quotation, please try again")

    def get_quotation_ids(self, requisition_id, supplier_id):
        try:
            self.__cursor.execute("""select quotation_id from quotations where requisition_id = %s and supplier_id = %s""",
                          (requisition_id, supplier_id, ))
            res = self.__cursor.fetchall()
            if len(res) > 0:
                quotation_ids = [x['quotation_id'] for x in res]
            else:
                quotation_ids = []
            return quotation_ids

        except mysql.connector.Error as error:
            log = Logger(module_name='QuotationOps', function_name='get_quotation_ids()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='QuotationOps', function_name='get_quotation_ids()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def get_active_quotations_for_requisition(self, requisition_id, status=True):
        try:
            self.__cursor.execute("""select * from quotations where requisition_id = %s and status = %s""",
                          (requisition_id, status, ))
            res = self.__cursor.fetchall()[0]
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='QuotationOps', function_name='get_quotations_for_requisition()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='QuotationOps', function_name='get_quotations_for_requisition()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def get_supplier_quotation_count(self, requisition_id, supplier_id):
        try:
            self.__cursor.execute("""select count(*) as quotation_count from quotations where requisition_id = %s and supplier_id = %s""",
                          (requisition_id, supplier_id, ))
            res = self.__cursor.fetchall()
            return res[0]['quotation_count']

        except mysql.connector.Error as error:
            log = Logger(module_name='QuotationOps', function_name='get_supplier_quotation_count()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='QuotationOps', function_name='get_supplier_quotation_count()')
            log.log(traceback.format_exc(), priority='highest')
            return False

# pprint(Quotation().get_quotations_count_for_requisition(1000))