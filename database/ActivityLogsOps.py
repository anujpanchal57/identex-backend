import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector

class ActivityLogs:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__activity_log = {}
        if self.__id != "":
            self.__cursor.execute("""select * from activity_logs where activity_id = %s""", (self.__id, ))
            self.__activity_log = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_activity(self, activity, done_by, type_of_user, operation_id, operation_type, ip_address):
        self.__activity_log['activity'] = activity
        self.__activity_log['done_by'] = done_by
        self.__activity_log['type_of_user'] = type_of_user
        self.__activity_log['operation_id'] = operation_id
        self.__activity_log['operation_type'] = operation_type
        self.__activity_log['ip_address'] = ip_address
        self.__activity_log['timestamp'] = GenericOps.get_current_timestamp()
        self.__activity_log['activity_id'] = self.insert(self.__activity_log)
        return self.__activity_log['activity_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.activity_logs_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO activity_logs (activity, done_by, type_of_user, operation_id, operation_type, 
                                    ip_address, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                  (values['activity'], values['done_by'], values['type_of_user'], values['operation_id'],
                                   values['operation_type'], values['ip_address'], values['timestamp']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='ActivityLogsOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='ActivityLogsOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

