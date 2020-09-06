import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class Invoice:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__invoice = {}
        if self.__id != "":
            self.__cursor.execute("""select * from invoices where invoice_id = %s""", (self.__id, ))
            self.__invoice = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_invoice(self, invoice_no, supplier_id, buyer_id, total_gst, total_amount, payment_details, due_date):
        self.__invoice['invoice_no'] = invoice_no
        self.__invoice['supplier_id'] = supplier_id
        self.__invoice['buyer_id'] = buyer_id
        self.__invoice['total_gst'] = total_gst
        self.__invoice['total_amount'] = total_amount
        self.__invoice['created_at'] = GenericOps.get_current_timestamp()
        self.__invoice['payment_details'] = payment_details
        self.__invoice['due_date'] = GenericOps.convert_datestring_to_timestamp(due_date) if due_date != "" else 0
        self.__invoice['invoice_id'] = self.insert(self.__invoice)
        return self.__invoice['invoice_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.invoices_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO invoices (invoice_no, supplier_id, buyer_id,
                        total_gst, total_amount, created_at, payment_details, due_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['invoice_no'], values['supplier_id'],
                                   values['buyer_id'], values['total_gst'], values['total_amount'],
                                   values['created_at'], values['payment_details'], values['due_date']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='InvoiceOps', function_name='insert()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException("Failed to add invoice, please try again")
        except Exception as e:
            log = Logger(module_name='InvoiceOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException("Failed to add invoice, please try again")

    def get_invoices(self, client_id, client_type, start_limit=0, end_limit=5):
        try:
            if client_type.lower() == "buyer":
                self.__cursor.execute("""select i.invoice_id, i.invoice_no, pm.product_id, pm.product_name, pm.product_category, 
                                        p.product_description, p.reqn_product_id, i.payment_status, i.due_date, i.total_amount
                                        from invoices as i
                                        join invoice_line_items as il
                                        on i.invoice_id = il.invoice_id
                                        join orders as o
                                        on il.order_id = o.order_id
                                        join products as p
                                        on o.reqn_product_id = p.reqn_product_id
                                        join product_master as pm
                                        on p.product_id = pm.product_id
                                        where i.buyer_id = %s
                                        order by i.due_date asc
                                        limit %s, %s""", (client_id, start_limit, end_limit))
                res = self.__cursor.fetchall()
                return res
            else:
                self.__cursor.execute("""select i.invoice_id, i.invoice_no, pm.product_id, pm.product_name, pm.product_category, 
                                        p.product_description, p.reqn_product_id, i.payment_status, i.due_date, i.total_amount
                                        from invoices as i
                                        join invoice_line_items as il
                                        on i.invoice_id = il.invoice_id
                                        join orders as o
                                        on il.order_id = o.order_id
                                        join products as p
                                        on o.reqn_product_id = p.reqn_product_id
                                        join product_master as pm
                                        on p.product_id = pm.product_id
                                        where i.supplier_id = %s
                                        order by i.due_date asc
                                        limit %s, %s""", (client_id, start_limit, end_limit))
                res = self.__cursor.fetchall()
                return res

        except mysql.connector.Error as error:
            log = Logger(module_name='InvoiceOps', function_name='get_invoices()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException("Failed to get invoices, please try again")
        except Exception as e:
            log = Logger(module_name='InvoiceOps', function_name='get_invoices()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException("Failed to get invoices, please try again")
