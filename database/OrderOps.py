import traceback
from pprint import pprint

import jwt
import mysql.connector
from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from exceptions import exceptions
from database.AuthorizationOps import Authorization

class Order:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__order = {}
        if self.__id != "":
            self.__cursor.execute("""select * from orders where order_id = %s""", (self.__id,))
            self.__order = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def get_order(self):
        return self.__order

    def get_grn_uploaded(self):
        return self.__order['grn_uploaded']

    def get_transaction_ref_no(self):
        return self.__order['transaction_ref_no']

    def get_payment_date(self):
        return self.__order['payment_date']

    def get_payment_status(self):
        return self.__order['payment_status']

    def get_quote_id(self):
        return self.__order['quote_id']

    def get_supplier_id(self):
        return self.__order['supplier_id']

    def get_po_no(self):
        return self.__order['po_no']

    def get_buyer_id(self):
        return self.__order['buyer_id']

    def get_reqn_product_id(self):
        return self.__order['reqn_product_id']

    def add_order(self, buyer_id, supplier_id, quote_id, reqn_product_id, remarks="", acquisition_id=0, acquisition_type="", po_no="", saved_amount=0):
        self.__order['buyer_id'] = buyer_id
        self.__order['supplier_id'] = supplier_id
        self.__order['quote_id'] = quote_id
        self.__order['reqn_product_id'] = reqn_product_id
        self.__order['acquisition_id'] = acquisition_id
        self.__order['acquisition_type'] = acquisition_type
        self.__order['po_no'] = po_no
        self.__order['created_at'] = GenericOps.get_current_timestamp()
        self.__order['remarks'] = remarks
        self.__order['saved_amount'] = saved_amount
        self.__order['order_id'] = self.insert(self.__order)
        return self.__order['order_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.orders_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO orders (buyer_id, supplier_id, po_no, acquisition_id, acquisition_type, 
                                    quote_id, reqn_product_id, created_at, remarks, saved_amount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['buyer_id'], values['supplier_id'], values['po_no'],
                                   values['acquisition_id'], values['acquisition_type'], values['quote_id'],
                                   values['reqn_product_id'], values['created_at'], values['remarks'], values['saved_amount']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to create order, please try again")
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to create order, please try again")

    def get_orders(self, client_id, client_type, request_type, acquisition_type="rfq", start_limit=0, end_limit=5):
        try:
            if client_type.lower() == "buyer":
                self.__cursor.execute("""select o.supplier_id, o.order_id, o.po_no, o.acquisition_id, o.acquisition_type, qu.delivery_time,
                                        r.currency, o.payment_status, o.order_status, o.grn_uploaded, o.payment_date, o.transaction_ref_no, 
                                        o.created_at, o.remarks, s.company_name as supplier_company_name, pm.product_name, idc.category_name, 
                                        idsc.sub_category_name, p.product_description, qu.amount, qu.per_unit, qu.gst
                                        from orders as o
                                        join requisitions as r
                                        on r.requisition_id = o.acquisition_id
                                        join suppliers as s 
                                        on o.supplier_id = s.supplier_id
                                        join quotes as qu
                                        on o.quote_id = qu.quote_id
                                        join products as p
                                        on o.reqn_product_id = p.reqn_product_id
                                        join product_master as pm
                                        on p.product_id = pm.product_id
                                        join idntx_category as idc
                                        on pm.product_category = idc.category_id
                                        join idntx_sub_categories as idsc
                                        on pm.product_sub_category = idsc.sub_category_id
                                        where o.buyer_id = %s and o.order_status = %s and o.acquisition_type = %s
                                        order by o.created_at desc
                                        limit %s, %s;""", (client_id, request_type, acquisition_type, start_limit, end_limit))

                res = self.__cursor.fetchall()
                return res
            else:
                self.__cursor.execute("""select o.buyer_id, b.company_name as buyer_company_name, o.order_id, o.po_no, o.acquisition_id, 
                                        r.currency, o.acquisition_type, qu.delivery_time,
                                        o.payment_status, o.order_status, o.grn_uploaded, o.payment_date, o.transaction_ref_no, 
                                        o.created_at, o.remarks, pm.product_name, idc.category_name, p.product_description, 
                                        qu.amount, qu.per_unit, qu.gst, idsc.sub_category_name
                                        from orders as o
                                        join requisitions as r
                                        on o.acquisition_id = r.requisition_id
                                        join buyers as b 
                                        on o.buyer_id = b.buyer_id
                                        join quotes as qu
                                        on o.quote_id = qu.quote_id
                                        join products as p
                                        on o.reqn_product_id = p.reqn_product_id
                                        join product_master as pm
                                        on p.product_id = pm.product_id
                                        join idntx_category as idc
                                        on pm.product_category = idc.category_id
                                        join idntx_sub_categories as idsc
                                        on pm.product_sub_category = idsc.sub_category_id
                                        where o.supplier_id = %s and o.order_status = %s and o.acquisition_type = %s
                                        order by o.created_at desc
                                        limit %s, %s;""", (client_id, request_type, acquisition_type, start_limit, end_limit))

                res = self.__cursor.fetchall()
                return res

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='get_orders()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to fetch orders, please try again")
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='get_orders()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to fetch orders, please try again")

    def get_order_product_details(self):
        try:
            self.__cursor.execute("""select o.reqn_product_id, p.product_id, pm.product_name, idc.category_name, 
                                    idsc.sub_category_name, p.product_description
                                    from orders as o
                                    join products as p
                                    on o.reqn_product_id = p.reqn_product_id
                                    join product_master as pm
                                    on p.product_id = pm.product_id
                                    join idntx_category as idc
                                    on pm.product_category = idc.category_id
                                    join idntx_sub_categories as idsc
                                    on pm.product_sub_category = idsc.sub_category_id
                                    where o.order_id = %s""", (self.__id, ))
            res = self.__cursor.fetchone()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='get_order_product_details()')
            log.log(str(error), priority='highest')
            return {}
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='get_order_product_details()')
            log.log(traceback.format_exc(), priority='highest')
            return {}

    def get_buyer_total_procurement(self, buyer_id):
        try:
            self.__cursor.execute("""select sum(qu.amount) as total_procurement
                                    from quotes as qu
                                    join orders as o
                                    on qu.quote_id = o.quote_id
                                    where o.buyer_id = %s and o.order_status in ('active', 'delivered')""", (buyer_id, ))
            res = self.__cursor.fetchone()['total_procurement']
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='get_buyer_total_procurement()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to get total procurement, please try again")
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='get_buyer_total_procurement()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to get total procurement, please try again")

    def get_supplier_orders_for_invoicing(self, buyer_id, supplier_id):
        try:
            self.__cursor.execute("""select o.order_id, o.buyer_id, o.po_no, qu.delivery_time, 
                                    qu.per_unit, qu.amount, qu.gst,
                                    o.created_at, pm.product_name, idc.category_name, idsc.sub_category_name,  
                                    p.product_description, qu.quantity, p.unit
                                    from orders as o
                                    join requisitions as r
                                    on o.acquisition_id = r.requisition_id
                                    join suppliers as s 
                                    on o.supplier_id = s.supplier_id
                                    join quotes as qu
                                    on o.quote_id = qu.quote_id
                                    join products as p
                                    on o.reqn_product_id = p.reqn_product_id
                                    join product_master as pm
                                    on p.product_id = pm.product_id
                                    join idntx_category as idc
                                    on pm.product_category = idc.category_id
                                    join idntx_sub_categories as idsc
                                    on pm.product_sub_category = idsc.sub_category_id
                                    where o.buyer_id = %s and o.supplier_id = %s and o.order_status in ('active', 'delivered')
                                    order by o.created_at desc""", (buyer_id, supplier_id, ))
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='get_supplier_orders_for_invoicing()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to fetch invoices, please try again")
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='get_supplier_orders_for_invoicing()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to fetch invoices, please try again")

    def get_supplier_buyers_list_for_orders(self, supplier_id):
        try:
            self.__cursor.execute("""select distinct o.buyer_id, b.company_name
                                    from orders as o
                                    join buyers as b
                                    on o.buyer_id = b.buyer_id
                                    where o.supplier_id = %s""",
                                  (supplier_id, ))
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='get_supplier_buyers_list_for_orders()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException('Failed to fetch list of buyers, please try again')
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='get_supplier_buyers_list_for_orders()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException('Failed to fetch list of buyers, please try again')

    def set_cancelled(self, cancelled):
        try:
            self.__order['cancelled'] = 1 if cancelled else 0
            self.__cursor.execute("""update orders set cancelled = %s where order_id = %s""", (cancelled, self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='set_cancelled()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to cancel order, please try again")
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='set_cancelled()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to cancel order, please try again")

    def set_grn_uploaded(self, grn_uploaded):
        try:
            self.__order['grn_uploaded'] = 1 if grn_uploaded else 0
            self.__cursor.execute("""update orders set grn_uploaded = %s where order_id = %s""", (grn_uploaded, self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='set_grn_uploaded()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update GRN, please try again")
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='set_grn_uploaded()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update GRN, please try again")

    def set_delivery_date(self, delivery_date):
        try:
            self.__order['delivery_date'] = delivery_date
            self.__cursor.execute("""update orders set delivery_date = %s where order_id = %s""", (delivery_date, self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='set_delivery_date()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update GRN, please try again")
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='set_delivery_date()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update GRN, please try again")

    def set_order_status(self, order_status):
        try:
            self.__order['order_status'] = order_status
            self.__cursor.execute("""update orders set order_status = %s where order_id = %s""", (order_status, self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='set_order_status()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update order status, please try again")
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='set_order_status()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update order status, please try again")

    def set_payment_status(self, payment_status):
        try:
            self.__order['payment_status'] = payment_status
            self.__cursor.execute("""update orders set payment_status = %s where order_id = %s""", (payment_status, self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='set_payment_status()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update payment status, please try again")
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='set_payment_status()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update payment status, please try again")

    def set_payment_date(self, payment_date):
        try:
            self.__order['payment_date'] = payment_date
            self.__cursor.execute("""update orders set payment_date = %s where order_id = %s""", (payment_date, self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='set_payment_date()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update payment date, please try again")
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='set_payment_date()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update payment date, please try again")

    def set_transaction_ref_no(self, transaction_ref_no):
        try:
            self.__order['transaction_ref_no'] = transaction_ref_no
            self.__cursor.execute("""update orders set transaction_ref_no = %s where order_id = %s""", (transaction_ref_no, self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='set_transaction_ref_no()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update transaction reference number, please try again")
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='set_transaction_ref_no()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update transaction reference number, please try again")

    def set_po_no(self, po_no):
        try:
            self.__order['po_no'] = po_no
            self.__cursor.execute("""update orders set po_no = %s where order_id = %s""", (po_no, self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='set_po_no()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update PO number, please try again")
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='set_po_no()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException("Failed to update PO number, please try again")

    def get_order_lot(self):
        try:
            self.__cursor.execute("""select l.lot_name from orders as o
                                    join lots as l
                                    on o.acquisition_id = l.requisition_id
                                    where o.order_id = %s""", (self.__id, ))

            pprint(self.__cursor.fetchone())
            res = self.__cursor.fetchone()['lot_name']
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='get_order_lot()')
            log.log(str(error), priority='highest')
            return ""
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='get_order_lot()')
            log.log(traceback.format_exc(), priority='highest')
            return ""

    def update_payment(self, payment_date, transaction_ref_no, payment_status="paid"):
        try:
            self.__cursor.execute("""update orders set payment_date = %s, transaction_ref_no = %s, payment_status = %s
                                    where order_id = %s""", (payment_date, transaction_ref_no, payment_status, self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='OrderOps', function_name='update_payment()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException("Failed to update order status, please try again")
        except Exception as e:
            log = Logger(module_name='OrderOps', function_name='update_payment()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException("Failed to update order status, please try again")







