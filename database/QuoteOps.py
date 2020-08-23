import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

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

    def add_quote(self, quotation_id, charge_id, charge_name, quantity, gst, per_unit, amount, delivery_time, confirmed=False):
        self.__quote['quotation_id'] = quotation_id
        self.__quote['charge_id'] = charge_id
        self.__quote['charge_name'] = charge_name
        self.__quote['quantity'] = quantity
        self.__quote['gst'] = gst
        self.__quote['per_unit'] = per_unit
        self.__quote['amount'] = amount
        self.__quote['delivery_time'] = delivery_time
        self.__quote['confirmed'] = confirmed
        self.__quote['quote_id'] = self.insert(self.__quote)
        return self.__quote['quote_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.quotes_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO quotes (quotation_id, charge_id, charge_name, quantity, gst, per_unit, 
                                        amount, delivery_time, confirmed) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['quotation_id'], values['charge_id'], values['charge_name'], values['quantity'],
                                   values['gst'], values['per_unit'], values['amount'], values['delivery_time'],
                                   values['confirmed']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='QuoteOps', function_name='insert()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add quote(s), please try again')
        except Exception as e:
            log = Logger(module_name='QuoteOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add quote(s), please try again')

    def insert_many(self, values):
        try:
            self.__cursor.execute(Implementations.quotes_create_table)
            # Inserting the record in the table
            self.__cursor.executemany("""INSERT INTO quotes (quotation_id, charge_id, charge_name, quantity, gst, per_unit, 
                                        amount, delivery_time, confirmed) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", values)
            self.__sql.commit()
            last_row_id = self.__cursor.lastrowid
            result_ids = [last_row_id]
            for x in range(1, len(values)):
                result_ids.append(last_row_id + x)
            return result_ids

        except mysql.connector.Error as error:
            log = Logger(module_name='QuoteOps', function_name='insert_many()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add quote(s), please try again')
        except Exception as e:
            log = Logger(module_name='QuoteOps', function_name='insert_many()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add quote(s), please try again')

    def remove_quotes(self, quotation_ids):
        try:
            if isinstance(quotation_ids, int):
                self.__cursor.execute("""delete from quotes where quotation_id = %s""", (quotation_ids, ))
            else:
                self.__cursor.execute("""delete from quotes where quotation_id in %s""", (quotation_ids, ))

            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='QuoteOps', function_name='remove_quotes()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to remove quote(s), please try again')
        except Exception as e:
            log = Logger(module_name='QuoteOps', function_name='remove_quotes()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to remove quote(s), please try again')

    def get_supplier_quotes_for_requisition(self, requisition_id, charge_id, status=True):
        try:
            self.__cursor.execute("""select s.company_name as supplier_company_name, s.supplier_id, qu.amount, qu.delivery_time, q.quote_validity,
                                    qu.charge_id as product_id
                                    from suppliers as s
                                    join quotations as q
                                    on s.supplier_id = q.supplier_id
                                    join quotes as qu
                                    on q.quotation_id = qu.quotation_id
                                    where q.requisition_id = %s
                                    and q.status = %s
                                    and qu.charge_id = %s
                                    order by amount asc;""", (requisition_id, status, charge_id))
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='QuoteOps', function_name='get_supplier_quotes_for_requisition()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='QuoteOps', function_name='get_supplier_quotes_for_requisition()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def get_quotes_by_category(self, requisition_id, charge_id, category="cheapest", status=True):
        try:
            if category.lower() == "cheapest":
                self.__cursor.execute("""select s.company_name as supplier_company_name, s.supplier_id, qu.amount, qu.delivery_time, q.quote_validity
                                        from suppliers as s
                                        join quotations as q
                                        on s.supplier_id = q.supplier_id
                                        join quotes as qu
                                        on q.quotation_id = qu.quotation_id
                                        where q.requisition_id = %s
                                        and q.status = %s 
                                        and qu.charge_id = %s
                                        order by qu.amount asc
                                        limit 0, 1;""", (requisition_id, status, charge_id))
                res = self.__cursor.fetchall()[0]
                return res
            elif category.lower() == "fastest":
                self.__cursor.execute("""select s.company_name as supplier_company_name, s.supplier_id, qu.amount, qu.delivery_time, q.quote_validity
                                        from suppliers as s
                                        join quotations as q
                                        on s.supplier_id = q.supplier_id
                                        join quotes as qu
                                        on q.quotation_id = qu.quotation_id
                                        where q.requisition_id = %s
                                        and q.status = %s 
                                        and qu.charge_id = %s
                                        order by qu.delivery_time asc
                                        limit 0, 1;""", (requisition_id, status, charge_id))
                res = self.__cursor.fetchall()[0]
                return res

        except mysql.connector.Error as error:
            log = Logger(module_name='QuoteOps', function_name='get_quotes_by_category()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='QuoteOps', function_name='get_quotes_by_category()')
            log.log(traceback.format_exc(), priority='highest')
            return []

# pprint(Quote().insert_many([(1000, 1000, 'ABCD', 2, 18, 1000.23, 1180.2326),
#  (1000, 1001, 'DEC', 3, 18, 2000.265, 2360.12354)]))