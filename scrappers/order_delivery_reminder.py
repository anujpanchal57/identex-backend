import os
import sys
from datetime import datetime, timezone
from pprint import pprint
from multiprocessing import Process


app_name = '/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1])
sys.path.append(app_name)

from utility import DBConnectivity, conf
from functionality.EmailNotifications import send_template_mail
from functionality.GenericOps import get_current_timestamp
# in seconds
execution_time_gap_1 = 86400
alert_time_1 = 86400


def order_delivery_reminder():
    sql = DBConnectivity.create_sql_connection()
    cursor = sql.cursor(dictionary=True)
    cursor.execute("""SELECT * FROM `buyers`""")
    all_buyers = cursor.fetchall()
    for buyer in all_buyers:
        cursor.execute("""SELECT * FROM `orders` WHERE `order_status` IN ('active') and `buyer_id` = %s""",
                       (buyer['buyer_id'],))
        for active_order in cursor.fetchall():
            cursor.execute("""SELECT * FROM `quotes` WHERE `quote_id` = %s""",
                       (active_order['quote_id'], ))
            quote = cursor.fetchone()
            delivery_days = (quote['delivery_time']) * 24 * 60 * 60
            if get_current_timestamp() < active_order['created_at'] + delivery_days <= get_current_timestamp() + 24 * 3600:
                cursor.execute("""SELECT * FROM `s_users` WHERE `supplier_id` = %s""",
                               (active_order['supplier_id'], ))
                suppliers = []
                supplier_name = ""
                for s_user in cursor.fetchall():
                    supplier_name = s_user['name'].split(' ')[0]
                    suppliers.append(s_user['email'])
                cursor.execute("""SELECT * FROM `b_users` WHERE `buyer_id` = %s""",
                               (buyer['buyer_id'],))
                buyers = []
                for b_user in cursor.fetchall():
                    buyers.append(b_user['email'])
                p = Process(target=send_template_mail, kwargs={
                    "subject": conf.email_endpoints['supplier']['order_delivery_reminder']['subject'].format(
                        quote['charge_name'], buyer['company_name']),
                    "template": conf.email_endpoints['supplier']['order_delivery_reminder']['template_id'],
                    "cc": buyers,
                    "recipients": suppliers,
                    "USER": supplier_name,
                    "ORDER_ID": active_order['order_id'],
                    "PRODUCT_NAME": quote['charge_name'],
                    "BUYER_COMPANY_NAME": buyer['company_name']
                })
                p.start()
            # print("RFQ:{} - {}".format(open_rfq['requisition_id'], open_rfq['request_type']))


order_delivery_reminder()
