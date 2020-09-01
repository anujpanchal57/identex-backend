import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class Requisition:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__requisition = {}
        if self.__id != "":
            self.__cursor.execute("""select * from requisitions where requisition_id = %s""", (self.__id, ))
            self.__requisition = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_requisition(self, requisition_name, buyer_id, timezone, currency, deadline, utc_deadline, tnc="", request_type="open",
                        cancelled=False, status=True, supplier_instructions="", submission_limit=3):
        self.__requisition['requisition_name'] = requisition_name
        self.__requisition['buyer_id'] = buyer_id
        self.__requisition['timezone'] = timezone
        self.__requisition['deadline'] = deadline
        self.__requisition['currency'] = currency
        self.__requisition['supplier_instructions'] = supplier_instructions
        self.__requisition['request_type'] = request_type
        self.__requisition['tnc'] = tnc
        self.__requisition['cancelled'] = cancelled
        self.__requisition['status'] = status
        self.__requisition['created_at'] = GenericOps.get_current_timestamp()
        self.__requisition['utc_deadline'] = utc_deadline
        self.__requisition['submission_limit'] = submission_limit
        self.__requisition['requisition_id'] = self.insert(self.__requisition)
        return self.__requisition['requisition_id']

    def insert(self, values, table="requisition_table"):
        try:
            self.__cursor.execute(Implementations.requisition_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO requisitions (buyer_id, requisition_name, timezone, currency, deadline, 
            utc_deadline, supplier_instructions, tnc, cancelled, request_type, status, created_at, submission_limit) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['buyer_id'], values['requisition_name'], values['timezone'], values['currency'],
                                   values['deadline'], values['utc_deadline'], values['supplier_instructions'], values['tnc'],
                                   values['cancelled'], values['request_type'], values['status'], values['created_at'],
                                   values['submission_limit']))
            requisition_id = self.__cursor.lastrowid

            # Adding an event for RFQ expiry
            event_id = 'rfq_' + str(requisition_id)
            request_type = "pending_approval"
            event_query = "create event if not exists " + event_id + " on schedule at '" + values['utc_deadline'] + "' do update `requisitions` set `request_type` = '" + request_type + "' where `requisition_id` = " + str(requisition_id) + " and `cancelled` = false"
            self.__cursor.execute(event_query)

            return requisition_id

        except mysql.connector.Error as error:
            log = Logger(module_name='RequisitionOps', function_name='insert()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add RFQ, please try again')
        except Exception as e:
            log = Logger(module_name='RequisitionOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add RFQ, please try again')

    def get_rfq(self, buyer_id):
        try:
            self.__cursor.execute("""select * from requisitions as r join lots as l on r.requisition_id = l.requisition_id and r.buyer_id = %s;""", (buyer_id, ))
            res = self.__cursor.fetchall()
            self.__sql.commit()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='RequisitionOps', function_name='get_rfq()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='RequisitionOps', function_name='get_rfq()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def cancel_rfq(self):
        try:
            self.__cursor.execute("""update requisitions set cancelled = true, request_type = 'cancelled' where requisition_id = %s""", (self.__id, ))
            self.__sql.commit()
            event_id = "rfq_" + str(self.__id)
            drop_query = "DROP EVENT if exists " + event_id
            self.__cursor.execute(drop_query)
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='RequisitionOps', function_name='cancel_rfq()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to cancel RFQ, please try again')
        except Exception as e:
            log = Logger(module_name='RequisitionOps', function_name='cancel_rfq()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to cancel RFQ, please try again')

    def get_deadline(self):
        return self.__requisition['deadline']

    def get_utc_deadline(self):
        return self.__requisition['utc_deadline']

    def get_requisition(self):
        return self.__requisition

    def get_cancelled(self):
        return self.__requisition['cancelled']

    def get_request_type(self):
        return self.__requisition['request_type']

    def get_timezone(self):
        return self.__requisition['timezone']

    def get_submission_limit(self):
        return self.__requisition['submission_limit']

    def update_deadline(self, deadline, utc_deadline):
        try:
            self.__requisition['deadline'] = deadline
            # Updating the request type to open, if it is pending for approval
            if self.__requisition['request_type'].lower() == "pending_approval":
                self.__cursor.execute("""update requisitions set request_type = 'open' where requisition_id = %s""", (self.__id, ))
                self.__sql.commit()

            # Updating the deadline in requisitions table
            self.__cursor.execute("""update requisitions set deadline = %s where requisition_id = %s""",
                                  (deadline, self.__id, ))

            self.__cursor.execute("""update requisitions set utc_deadline = %s where requisition_id = %s""",
                                  (utc_deadline, self.__id, ))

            # Drop the existing mysql event for updating the request type
            event_id = 'rfq_' + str(self.__id)
            drop_query = "DROP EVENT if exists " + event_id
            self.__cursor.execute(drop_query)

            # Create a new event for changing the request time on deadline completion
            event_id = 'rfq_' + str(self.__id)
            request_type = "pending_approval"
            event_query = "create event if not exists " + event_id + " on schedule at '" + utc_deadline + "' do update `requisitions` set `request_type` = '" + request_type + "' where `requisition_id` = " + str(self.__id) + " and `cancelled` = false"
            self.__cursor.execute(event_query)

            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='RequisitionOps', function_name='update_deadline()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to update deadline, please try again')
        except Exception as e:
            log = Logger(module_name='RequisitionOps', function_name='update_deadline()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to update deadline, please try again')

# pprint(Requisition(1000).cancel_rfq())
# pprint(Requisition().get_rfq(1000))
# pprint(Requisition().add_requisition(requisition_name="ABC", buyer_id=1000, timezone="asia/calcutta", currency="inr", deadline=6513216854))