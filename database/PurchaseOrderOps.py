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

    def get_po_no(self):
        return self.__po['po_no']

    def add_po(self, po_no, buyer_id, supplier_id, acquisition_id, acquisition_type, order_date, total_amount, total_gst,
               unit_currency, supplier_details, delivery_details, payment_terms, freight_included, prepared_by, approved_by,
               notes='', tnc='', po_metadata='', total_in_words=''):
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
        self.__po['created_at'] = GenericOps.get_current_timestamp()
        self.__po['po_metadata'] = po_metadata
        self.__po['total_in_words'] = total_in_words
        self.__po['po_id'] = self.insert(self.__po)
        return self.__po['po_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.po_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO purchase_orders (po_no, buyer_id, supplier_id, acquisition_id, acquisition_type, 
                                        order_date, unit_currency, total_amount, total_gst, notes, tnc, supplier_gst_no, 
                                        supplier_address, supplier_pincode, supplier_country, delivery_address, delivery_pincode, 
                                        delivery_country, payment_terms, freight_included, prepared_by, approved_by, created_at, 
                                        po_metadata, total_in_words) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                        %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['po_no'], values['buyer_id'], values['supplier_id'],
                                   values['acquisition_id'], values['acquisition_type'], values['order_date'], values['unit_currency'],
                                   values['total_amount'], values['total_gst'], values['notes'], values['tnc'],
                                   values['supplier_gst_no'], values['supplier_address'], values['supplier_pincode'],
                                   values['supplier_country'], values['delivery_address'], values['delivery_pincode'],
                                   values['delivery_country'], values['payment_terms'], values['freight_included'],
                                   values['prepared_by'], values['approved_by'], values['created_at'], values['po_metadata'],
                                   values['total_in_words']))
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

    def set_po_status(self, po_status):
        try:
            self.__po['po_status'] = po_status
            self.__cursor.execute("""update purchase_orders set po_status = %s where po_id = %s""", (po_status, self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='PurchaseOrderOps', function_name='set_po_status()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update PO status, please try again")
        except Exception as e:
            log = Logger(module_name='PurchaseOrderOps', function_name='set_po_status()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update PO status, please try again")

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

    def get_purchase_orders(self, client_id, client_type, request_type="active", start_limit=0, end_limit=5):
        try:
            if client_type.lower() == "buyer":
                self.__cursor.execute("""select po.po_id, po.po_no, po.buyer_id, po.supplier_id, po.acquisition_id, po.acquisition_type, 
                                        po.order_date, po.unit_currency, po.total_amount, po.total_gst, po.tnc, po.po_url, 
                                        po.po_status, po.payment_status, po.delivery_status, s.company_name as supplier_company_name
                                        from purchase_orders as po
                                        join suppliers as s
                                        on po.supplier_id = s.supplier_id
                                        where po.buyer_id = %s and po.po_status = %s
                                        order by po.created_at desc
                                        limit %s, %s""", (client_id, request_type, start_limit, end_limit))
                res = self.__cursor.fetchall()
                if res is None:
                    return []
                return res
            else:
                self.__cursor.execute("""select po.po_id, po.po_no, po.buyer_id, po.supplier_id, po.acquisition_id, po.acquisition_type, 
                                        po.order_date, po.unit_currency, po.total_amount, po.total_gst, po.tnc, po.po_url, 
                                        po.po_status, po.payment_status, po.delivery_status, b.company_name as buyer_company_name
                                        from purchase_orders as po
                                        join buyers as b
                                        on po.buyer_id = b.buyer_id
                                        where po.supplier_id = %s and po.po_status = %s
                                        order by po.created_at desc
                                        limit %s, %s""", (client_id, request_type, start_limit, end_limit))
                res = self.__cursor.fetchall()
                if res is None:
                    return []
                return res

        except mysql.connector.Error as error:
            log = Logger(module_name='PurchaseOrderOps', function_name='get_purchase_orders()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to fetch purchase orders, please try again")
        except Exception as e:
            log = Logger(module_name='PurchaseOrderOps', function_name='get_purchase_orders()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to fetch purchase orders, please try again")

    def get_buyer_purchase_orders_count(self, buyer_id, request_type="active"):
        try:
            self.__cursor.execute("""select count(*) as total_count from purchase_orders
                                    where buyer_id = %s and po_status = %s""", (buyer_id, request_type))
            res = self.__cursor.fetchone()
            if res is None:
                return 0
            return res['total_count']

        except mysql.connector.Error as error:
            log = Logger(module_name='PurchaseOrderOps', function_name='get_buyer_purchase_orders_count()')
            log.log(str(error), priority='highest')
            return 0
        except Exception as e:
            log = Logger(module_name='PurchaseOrderOps', function_name='get_buyer_purchase_orders_count()')
            log.log(traceback.format_exc(), priority='highest')
            return 0

    def get_supplier_purchase_orders_count(self, supplier_id, request_type="active"):
        try:
            self.__cursor.execute("""select count(*) as total_count from purchase_orders
                                    where supplier_id = %s and po_status = %s""", (supplier_id, request_type))
            res = self.__cursor.fetchone()
            if res is None:
                return 0
            return res['total_count']

        except mysql.connector.Error as error:
            log = Logger(module_name='PurchaseOrderOps', function_name='get_supplier_purchase_orders_count()')
            log.log(str(error), priority='highest')
            return 0
        except Exception as e:
            log = Logger(module_name='PurchaseOrderOps', function_name='get_supplier_purchase_orders_count()')
            log.log(traceback.format_exc(), priority='highest')
            return 0

    def update_po_url(self, file_link):
        self.__po['po_url'] = file_link
        self.__cursor.execute("""update purchase_orders set po_url = %s where po_id = %s""", (file_link, self.__id))
        self.__sql.commit()
        return True

    def set_delivery_status(self, delivery_status):
        try:
            self.__po['delivery_status'] = delivery_status
            self.__cursor.execute("""update purchase_orders set delivery_status = %s where po_id = %s""",
                                  (delivery_status, self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='PurchaseOrderOps', function_name='set_delivery_status()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update PO delivery status, please try again")
        except Exception as e:
            log = Logger(module_name='PurchaseOrderOps', function_name='set_delivery_status()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update PO delivery status, please try again")

