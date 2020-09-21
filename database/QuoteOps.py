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

    def get_amount(self):
        return self.__quote['amount']

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

    def remove_quotes(self, quotation_id):
        try:
            self.__cursor.execute("""delete from quotes where quotation_id = %s""", (quotation_id, ))
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
                                    qu.charge_id, qu.quote_id, qu.confirmed, qu.charge_name, qu.quantity, qu.gst, qu.per_unit 
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

    def get_highest_quote_for_product(self, requisition_id, buyer_id, charge_id):
        try:
            self.__cursor.execute("""select max(qu.amount) as max_amount
                                    from requisitions as r
                                    join quotations as q
                                    on r.requisition_id = q.requisition_id
                                    join quotes as qu
                                    on q.quotation_id = qu.quotation_id
                                    where r.requisition_id = %s and r.buyer_id = %s and qu.charge_id = %s""",
                                  (requisition_id, buyer_id, charge_id))
            res = self.__cursor.fetchone()['max_amount']
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='QuoteOps', function_name='get_quotes_for_product()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='QuoteOps', function_name='get_quotes_for_product()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def get_quotes_by_category(self, requisition_id, charge_id, category="cheapest", status=True):
        try:
            if category.lower() == "cheapest":
                self.__cursor.execute("""select s.company_name as supplier_company_name, s.supplier_id, qu.amount, qu.delivery_time, q.quote_validity,
                                        qu.quote_id
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
                self.__cursor.execute("""select s.company_name as supplier_company_name, s.supplier_id, qu.amount, qu.delivery_time, q.quote_validity,
                                        qu.quote_id
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

    def is_product_quote_confirmed(self, charge_id, confirmed=True):
        try:
            self.__cursor.execute("select confirmed from quotes where charge_id = %s and confirmed = %s", (charge_id, confirmed, ))
            res = self.__cursor.fetchall()
            return True if len(res) > 0 else False

        except mysql.connector.Error as error:
            log = Logger(module_name='QuoteOps', function_name='is_product_quote_confirmed()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='QuoteOps', function_name='is_product_quote_confirmed()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def set_confirmed(self, confirmed):
        try:
            self.__quote['confirmed'] = confirmed
            self.__cursor.execute("""update quotes set confirmed = %s where quote_id = %s""", (confirmed, self.__id, ))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='QuoteOps', function_name='set_confirmed()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException('Failed to update product confirmation, please try again')
        except Exception as e:
            log = Logger(module_name='QuoteOps', function_name='set_confirmed()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException('Failed to update product confirmation, please try again')


# pprint(Quote().insert_many([(1000, 1000, 'ABCD', 2, 18, 1000.23, 1180.2326),
#  (1000, 1001, 'DEC', 3, 18, 2000.265, 2360.12354)]))
# pprint(Quote(1023).is_quote_confirmed())