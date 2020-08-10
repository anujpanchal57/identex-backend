import uuid
from pprint import pprint

import mysql.connector
from utility import DBConnectivity, Implementations
from utility import conf
from functionality import GenericOps, EmailNotifications

class Logger:

    def __init__(self,module_name,function_name):
        self.__module_name = module_name
        self.__function_name = function_name
        self.__log_id = str(uuid.uuid4())
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def log(self,error,priority='high', table="log_table"):
        try:
            # Checking whether the table exists or not
            self.__cursor.execute(Implementations.logs_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO logs (log_id, function_name, module_name, message, priority, timestamp) VALUES (%s, %s, %s, %s, %s, %s)""",
                                  (self.__log_id, self.__function_name, self.__module_name,
                                   error, priority, GenericOps.get_current_timestamp()))
            self.__sql.commit()
            return True
        except mysql.connector.Error as error:
            # Email the error
            message = "<h1>Error in logger: </h1><br><p>{}</p>".format(error)
            EmailNotifications.send_mail(subject="Error in logger", message=message, recipients=["anuj.panchal@identex.io"])
            return False

# pprint(Logger(module_name="/buyer/forgot-password/auth", function_name="buyer_forgot_password_auth()").log("adsferwvwervwfvsdfv"))