import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class InvoiceLineItem:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__invoice_lt = {}
        if self.__id != "":
            self.__cursor.execute("""select * from invoice_line_items where line_item_id = %s""", (self.__id, ))
            self.__invoice_lt = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_line_item(self, invoice_id, order_id, quantity, gst, per_unit, amount, unit_currency="inr"):
        self.__invoice_lt['invoice_id'] = invoice_id
        self.__invoice_lt['order_id'] = order_id
        self.__invoice_lt['quantity'] = quantity
        self.__invoice_lt['gst'] = gst
        self.__invoice_lt['per_unit'] = per_unit
        self.__invoice_lt['amount'] = amount
        self.__invoice_lt['unit_currency'] = unit_currency
        self.__invoice_lt['line_item_id'] = self.insert(self.__invoice_lt)
        return self.__invoice_lt['line_item_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.invoice_line_items_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO invoice_line_items (invoice_id, order_id, quantity, gst, per_unit, amount, 
                                        unit_currency) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                  (values['invoice_id'], values['order_id'], values['quantity'],
                                   values['gst'],
                                   values['per_unit'], values['amount'], values['unit_currency']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='InvoiceLineItemOps', function_name='insert()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add line item(s), please try again')
        except Exception as e:
            log = Logger(module_name='InvoiceLineItemOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add line item(s), please try again')

    def insert_many(self, values):
        try:
            self.__cursor.execute(Implementations.invoice_line_items_create_table)
            # Inserting the record in the table
            self.__cursor.executemany("""INSERT INTO invoice_line_items (invoice_id, order_id, quantity, gst, per_unit, amount, 
                                        unit_currency) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)""", values)
            self.__sql.commit()
            last_row_id = self.__cursor.lastrowid
            result_ids = [last_row_id]
            for x in range(1, len(values)):
                result_ids.append(last_row_id + x)
            return result_ids

        except mysql.connector.Error as error:
            log = Logger(module_name='InvoiceLineItemOps', function_name='insert_many()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add line item(s), please try again')
        except Exception as e:
            log = Logger(module_name='InvoiceLineItemOps', function_name='insert_many()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add line item(s), please try again')