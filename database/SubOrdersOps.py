import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class SubOrder:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__sub_order = {}
        if self.__id != "":
            self.__cursor.execute("""select * from sub_orders where order_id = %s""", (self.__id, ))
            self.__sub_order = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def get_qty_received(self):
        return self.__sub_order['qty_received']

    def get_quantity(self):
        return self.__sub_order['quantity']

    def get_delivery_status(self):
        return self.__sub_order['delivery_status']

    def get_rem_quantity(self):
        return GenericOps.round_of(self.__sub_order['quantity'] - self.__sub_order['qty_received'])

    def insert_many(self, values):
        try:
            self.__cursor.execute(Implementations.sub_orders_create_table)
            # Inserting the record in the table
            self.__cursor.executemany("""INSERT INTO sub_orders (po_id, product_id, created_at, product_description, 
                                        quantity, unit, gst, per_unit, amount, delivery_time) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", values)
            self.__sql.commit()
            last_row_id = self.__cursor.lastrowid
            result_ids = [last_row_id]
            for x in range(1, len(values)):
                result_ids.append(last_row_id + x)
            return result_ids

        except mysql.connector.Error as error:
            log = Logger(module_name='SubOrderOps', function_name='insert_many()')
            log.log(str(error), priority='critical')
            raise exceptions.IncompleteRequestException('Failed to order line items, please try again')
        except Exception as e:
            log = Logger(module_name='SubOrderOps', function_name='insert_many()')
            log.log(traceback.format_exc(), priority='critical')
            raise exceptions.IncompleteRequestException('Failed to add order line items, please try again')

    def get_sub_order_by_po_id(self, po_id):
        try:
            self.__cursor.execute("""select sb.order_id, sb.po_id, sb.product_id, sb.payment_status, 
                                    sb.order_status, sb.product_description, sb.quantity, sb.unit, sb.gst, 
                                    sb.per_unit, sb.amount, sb.delivery_time, sb.qty_received, sb.delivery_status, 
                                    sb.quantity - sb.qty_received as rem_quantity, pm.product_name
                                    from sub_orders as sb
                                    join product_master as pm
                                    on sb.product_id = pm.product_id
                                    where sb.po_id = %s""", (po_id, ))
            res = self.__cursor.fetchall()
            if res is None:
                return []
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='SubOrderOps', function_name='get_sub_order_by_po_id()')
            log.log(str(error), priority='critical')
            raise exceptions.IncompleteRequestException('Failed to fetch PO line items, please try again')
        except Exception as e:
            log = Logger(module_name='SubOrderOps', function_name='get_sub_order_by_po_id()')
            log.log(traceback.format_exc(), priority='critical')
            raise exceptions.IncompleteRequestException('Failed to fetch PO line items, please try again')

    def update_order_delivery(self, qty_recd, order_status, delivery_status):
        try:
            qty_recd += self.get_qty_received()
            self.__sub_order['qty_received'], self.__sub_order['order_status'], self.__sub_order['delivery_status'] = qty_recd, order_status, delivery_status
            self.__cursor.execute("""update sub_orders set qty_received = %s, order_status = %s, delivery_status = %s 
                                    where order_id = %s""", (qty_recd, order_status, delivery_status, self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='SubOrderOps', function_name='update_order_delivery()')
            log.log(str(error), priority='critical')
            raise exceptions.IncompleteRequestException('Failed to record order delivery, please try again')
        except Exception as e:
            log = Logger(module_name='SubOrderOps', function_name='update_order_delivery()')
            log.log(traceback.format_exc(), priority='critical')
            raise exceptions.IncompleteRequestException('Failed to record order delivery, please try again')


# pprint(SubOrder().get_sub_order_by_po_id(1015))