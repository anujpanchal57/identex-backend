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

    def add_po(self, po_no, buyer_id, supplier_id, acquisition_id, acquisition_type, order_date, total_amount, total_gst,
               unit_currency, supplier_details, delivery_details, payment_terms, freight_included, prepared_by, approved_by,
               notes='', tnc=''):
        self.__po['po_no'], self.__po['buyer_id'], self.__po['supplier_id'] = po_no, buyer_id, supplier_id
        self.__po['total_amount'], self.__po['total_gst'] = total_amount, total_gst
        self.__po['notes'], self.__po['tnc'] = notes, tnc
        self.__po['acquisition_id'], self.__po['acquisition_type'] = acquisition_id, acquisition_type
        self.__po['order_date'], self.__po['unit_currency'] = order_date, unit_currency
        self.__po['supplier_gst_no'] = supplier_details['gst_no'] if 'gst_no' in supplier_details else ''
        self.__po['supplier_address'] = supplier_details['business_address'] if 'business_address' in supplier_details else ''
        self.__po['supplier_pincode'] = supplier_details['pincode'] if 'pincode' in supplier_details else ''
        self.__po['supplier_country'] = supplier_details['country'] if 'country' in supplier_details else ''
        self.__po['delivery_address'] = delivery_details['company_address'] if 'company_address' in delivery_details else ''
        self.__po['delivery_pincode'] = delivery_details['pincode'] if 'pincode' in delivery_details else ''
        self.__po['delivery_country'] = delivery_details['country'] if 'country' in delivery_details else ''
        self.__po['payment_terms'], self.__po['freight_included'] = payment_terms, freight_included
        self.__po['prepared_by'], self.__po['approved_by'] = prepared_by, approved_by
        self.__po['po_id'] = self.insert(self.__po)
        return self.__po['po_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.po_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO purchase_orders (po_no, buyer_id, supplier_id, acquisition_id, acquisition_type, 
                                        order_date, unit_currency, total_amount, total_gst, notes, tnc, supplier_gst_no, 
                                        supplier_address, supplier_pincode, supplier_country, delivery_address, delivery_pincode, 
                                        delivery_country, payment_terms, freight_included, prepared_by, approved_by) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                        %s, %s, %s, %s)""",
                                  (values['po_no'], values['buyer_id'], values['supplier_id'],
                                   values['acquisition_id'], values['acquisition_type'], values['order_date'], values['unit_currency'],
                                   values['total_amount'], values['total_gst'], values['notes'], values['tnc'],
                                   values['supplier_gst_no'], values['supplier_address'], values['supplier_pincode'],
                                   values['supplier_country'], values['delivery_address'], values['delivery_pincode'],
                                   values['delivery_country'], values['payment_terms'], values['freight_included'],
                                   values['prepared_by'], values['approved_by']))
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

    def get_total_amount_for_acquisition(self, acquisition_id, acquisition_type="rfq"):
        try:
            self.__cursor.execute("""select sum(total_amount) as total_amount from purchase_orders where acquisition_id = %s and acquisition_type = %s""",
                                  (acquisition_id, acquisition_type))
            res = self.__cursor.fetchone()
            if res is None:
                return 0
            return res['total_amount']

        except mysql.connector.Error as error:
            log = Logger(module_name='PurchaseOrderOps', function_name='get_total_amount_for_acquisition()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to fetch total amount, please try again")
        except Exception as e:
            log = Logger(module_name='PurchaseOrderOps', function_name='get_total_amount_for_acquisition()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to fetch total amount, please try again")

    def get_total_gst_for_acquisition(self, acquisition_id, acquisition_type="rfq"):
        try:
            self.__cursor.execute("""select sum(total_gst) as total_gst from purchase_orders where acquisition_id = %s and acquisition_type = %s""",
                                  (acquisition_id, acquisition_type))
            res = self.__cursor.fetchone()
            if res is None:
                return 0
            return res['total_gst']

        except mysql.connector.Error as error:
            log = Logger(module_name='PurchaseOrderOps', function_name='get_total_gst_for_acquisition()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to fetch total GST, please try again")
        except Exception as e:
            log = Logger(module_name='PurchaseOrderOps', function_name='get_total_gst_for_acquisition()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to fetch total GST, please try again")

