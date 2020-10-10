import os
import sys
from datetime import datetime, timezone
from pprint import pprint
from multiprocessing import Process

from functionality.EmailNotifications import send_template_mail

app_name = '/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1])
sys.path.append(app_name)
from utility import DBConnectivity, conf

# in seconds
execution_time_gap_1 = 600
alert_time_1 = 7200

def rfq_close_reminder():
    sql = DBConnectivity.create_sql_connection()
    cursor = sql.cursor(dictionary=True)
    cursor.execute("""SELECT * FROM `buyers`""")
    all_buyers = cursor.fetchall()
    for buyer in all_buyers:
        # print(buyer['buyer_id'])
        cursor.execute("""SELECT * FROM `requisitions` WHERE `request_type` IN ('open') and `buyer_id` = %s""", (buyer['buyer_id'], ))
        for open_rfq in cursor.fetchall():
            deadline_date, deadline_time = open_rfq['utc_deadline'].split(' ')
            deadline_date = deadline_date.split('-')
            deadline_time = deadline_time.split(':')
            deadline_timestamp = int(datetime.timestamp(datetime(year=int(deadline_date[0]), month=int(deadline_date[1]), day=int(deadline_date[2]), hour=int(deadline_time[0]), minute=int(deadline_time[1]), tzinfo=timezone.utc)))
            timestamp_now_utc = datetime.timestamp(datetime.now(timezone.utc))
            if int(timestamp_now_utc + alert_time_1) < deadline_timestamp <= int(timestamp_now_utc + alert_time_1 + execution_time_gap_1):
                cursor.execute("SELECT * FROM `invited_suppliers` WHERE `operation_id`= %s and `operation_type` = 'rfq'", (open_rfq['requisition_id'],))
                invited_suppliers = cursor.fetchall()
                for supplier in invited_suppliers:
                    cursor.execute("""SELECT * FROM `s_users` WHERE `supplier_id` = %s""",
                                   (supplier['supplier_id'], ))
                    suppliers = []
                    supplier_name = ""
                    for s_user in cursor.fetchall():
                        supplier_name = s_user['name'].split(' ')[0]
                        suppliers.append(s_user['email'])
                    p = Process(target=send_template_mail, kwargs={
                        "subject": conf.email_endpoints['supplier']['rfq_close_reminder']['subject'].format(open_rfq['requisition_id'], buyer['company_name'], open_rfq['requisition_name']),
                        "template": conf.email_endpoints['supplier']['rfq_close_reminder']['template_id'],
                        "recipients": suppliers,
                        "USER": supplier_name,
                        "LOT_NAME": open_rfq['requisition_name'],
                        "OPERATION_ID": open_rfq['requisition_id'],
                        "BUYER_COMPANY_NAME": buyer['company_name'],
                        "LINK": conf.SUPPLIERS_ENDPOINT + conf.email_endpoints['supplier']['rfq_close_reminder']['page_url']
                    })
                    p.start()
            # print("RFQ:{} - {}".format(open_rfq['requisition_id'], open_rfq['request_type']))

rfq_close_reminder()