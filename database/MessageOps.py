import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector

class Message:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__message = {}
        if self.__id != "":
            self.__cursor.execute("""select * from messages where message_id = %s""", (self.__id, ))
            self.__message = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def get_message(self):
        return self.__message

    def add_message(self, operation_id, operation_type, message, sent_by, sender_user, sender, received_by, receiver, status=False):
        self.__message['operation_id'] = operation_id
        self.__message['operation_type'] = operation_type
        self.__message['message'] = message
        self.__message['sent_on'] = GenericOps.get_current_timestamp()
        self.__message['sent_by'] = sent_by
        self.__message['sender_user'] = sender_user
        self.__message['sender'] = sender
        self.__message['received_by'] = received_by
        self.__message['receiver'] = receiver
        self.__message['status'] = status
        self.__message['message_id'] = self.insert(self.__message)
        return self.__message['message_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.messages_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO messages (operation_id, operation_type, message, sent_on, sender_user, sent_by, 
                                    sender, received_by, receiver, status) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['operation_id'], values['operation_type'], values['message'], values['sent_on'], values['sender_user'],
                                   values['sent_by'], values['sender'], values['received_by'], values['receiver'], values['status']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='MessageOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='MessageOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def get_operation_messages(self, operation_id, operation_type, sent_by, sender, receiver_id, receiver_type, start_limit=0, end_limit=10):
        try:
            self.__cursor.execute("""select * from messages
                                                where operation_id = %s and operation_type = %s and 
                                                ((sent_by = %s and sender = %s) or (received_by = %s and receiver = %s)) 
                                                and ((sent_by = %s and sender = %s) or (received_by = %s and receiver = %s))  
                                                order by sent_on desc
                                                limit %s, %s;""",
                                  (operation_id, operation_type, sent_by, sender, sent_by, sender,
                                   receiver_id, receiver_type, receiver_id, receiver_type, start_limit, end_limit))
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='MessageOps', function_name='get_operation_messages()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='MessageOps', function_name='get_operation_messages()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def get_unread_messages(self, operation_id, operation_type, sent_by, sender, receiver_id, receiver_type):
        try:
            self.__cursor.execute("""select count(*) as unread from messages
                                    where operation_id = %s and operation_type = %s and sender = %s and 
                                    receiver = %s and sent_by = %s and received_by = %s and status = false""",
                                  (operation_id, operation_type, sender, receiver_type, sent_by, receiver_id))
            unread = self.__cursor.fetchone()['unread']
            return unread

        except mysql.connector.Error as error:
            log = Logger(module_name='MessageOps', function_name='get_unread_messages()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='MessageOps', function_name='get_unread_messages()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def get_last_message(self, operation_id, operation_type, sent_by, sender, receiver_id, receiver_type, start_limit=0, end_limit=1):
        try:
            self.__cursor.execute("""select * from messages
                                    where operation_id = %s and operation_type = %s and 
                                    ((sent_by = %s and sender = %s) or (received_by = %s and receiver = %s)) 
                                    and ((sent_by = %s and sender = %s) or (received_by = %s and receiver = %s))  
                                    order by sent_on desc
                                    limit %s, %s;""",
                                  (operation_id, operation_type, sent_by, sender, sent_by, sender,
                                   receiver_id, receiver_type, receiver_id, receiver_type, start_limit, end_limit))
            res = self.__cursor.fetchone()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='MessageOps', function_name='get_last_message()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='MessageOps', function_name='get_last_message()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def get_total_unread_messages(self, operation_id, operation_type, receiver):
        try:
            self.__cursor.execute("""select count(*) as unread from messages
                                    where operation_id = %s and operation_type = %s and receiver = %s and status = false""",
                                  (operation_id, operation_type, receiver))
            unread = self.__cursor.fetchone()['unread']
            return unread

        except mysql.connector.Error as error:
            log = Logger(module_name='MessageOps', function_name='get_total_unread_messages()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='MessageOps', function_name='get_total_unread_messages()')
            log.log(traceback.format_exc(), priority='highest')
            return False

# pprint(Message().get_operation_messages(1000, "rfq_msg", 1000, "buyer", 1000, "supplier"))
# pprint(Message().get_unread_messages(1000, "rfq_msg", 1000, "supplier", 1000, "buyer"))
# pprint(Message().get_last_message(1000, "rfq_msg", 1000, "supplier", 1000, "buyer"))
# pprint(Message().get_total_unread_messages(1000, "rfq_msg", "supplier"))