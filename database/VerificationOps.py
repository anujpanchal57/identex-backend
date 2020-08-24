import traceback
from pprint import pprint
import mysql.connector
from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger

class Verification:
    def __init__(self, _id="", name=""):
        self.__id = _id
        self.__name = name
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__verification = {}
        if self.__id != "":
            self.__cursor.execute("""select * from verification_tokens where token_id = %s and token_name = %s""", (self.__id, self.__name, ))
            self.__verification = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_auth_token(self, token_id, user_id, user_type):
        self.__verification['token_id'] = token_id
        self.__verification['token_name'] = self.__name
        self.__verification['user_id'] = user_id
        self.__verification['user_type'] = user_type
        return self.insert(self.__verification)

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.verification_tokens_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO verification_tokens (token_id, token_name, user_id, user_type) VALUES (%s, %s, %s, %s)""",
                                  (values['token_id'], values['token_name'], values['user_id'], values['user_type']))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='VerificationOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='VerificationOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def verify_auth_token(self, user_type):
        self.__cursor.execute("select * from verification_tokens where token_id = %s and token_name = %s and user_type = %s",
                              (self.__id, self.__name, user_type))
        if len(self.__cursor.fetchall()) == 0:
            return False
        self.__cursor.execute("delete from verification_tokens where token_id = %s and token_name = %s and user_type = %s",
                              (self.__id, self.__name, user_type))
        self.__sql.commit()
        return True

    def is_valid_token(self):
        return True if self.__verification is not None else False

    def delete_verification_token(self):
        try:
            self.__cursor.execute("""delete from verification_tokens where token_id = %s and token_name = %s and user_type = %s""",
                (self.__id, self.__name, self.__verification['user_type']))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='VerificationOps', function_name='delete_verification_token()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='VerificationOps', function_name='delete_verification_token()')
            log.log(traceback.format_exc(), priority='highest')
            return False

