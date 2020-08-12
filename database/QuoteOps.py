import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector

class Quote:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__quote = {}
        if self.__id != "":
            self.__cursor.execute("""select * from quotes where quote_id = %s""", (self.__id, ))
            self.__quote = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_quote(self, quotation_id, charge_id, charge_name, quantity, gst, per_unit, amount):
        self.__quote['quotation_id'] = quotation_id
        self.__quote['charge_id'] = charge_id
        self.__quote['charge_name'] = charge_name
        self.__quote['quantity'] = quantity
        self.__quote['gst'] = gst
        self.__quote['per_unit'] = per_unit
        self.__quote['amount'] = amount
        self.__quote['quote_id'] = self.insert(self.__quote)
        return self.__quote['quote_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.quotes_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO quotes (quotation_id, charge_id, charge_name, quantity, gst, per_unit, amount) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                  (values['quotation_id'], values['charge_id'], values['charge_name'], values['quantity'],
                                   values['gst'], values['per_unit'], values['amount']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='QuoteOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='QuoteOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def insert_many(self, values):
        try:
            self.__cursor.execute(Implementations.quotes_create_table)
            # Inserting the record in the table
            self.__cursor.executemany("""INSERT INTO quotes (quotation_id, charge_id, charge_name, quantity, gst, per_unit, amount) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""", values)
            self.__sql.commit()
            last_row_id = self.__cursor.lastrowid
            result_ids = [last_row_id]
            for x in range(1, len(values)):
                result_ids.append(last_row_id + x)
            pprint(result_ids)
            return result_ids

        except mysql.connector.Error as error:
            log = Logger(module_name='QuoteOps', function_name='insert_many()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='QuoteOps', function_name='insert_many()')
            log.log(traceback.format_exc(), priority='highest')
            return False

# pprint(Quote().insert_many([(1000, 1000, 'ABCD', 2, 18, 1000.23, 1180.2326),
#  (1000, 1001, 'DEC', 3, 18, 2000.265, 2360.12354)]))