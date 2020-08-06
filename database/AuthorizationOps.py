import traceback

from functionality.Logger import Logger
from utility import DBConnectivity, conf, Implementations
from pprint import pprint
import mysql.connector

class Authorization:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__auth = {}
        if self.__id != "":
            self.__cursor.execute("""select * from authorizations where auth_id = %s""", (self.__id, ))
            self.__auth = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def login_user(self, auth_id, logged_in, entity_id, email, device_name, type):
        self.__auth['auth_id'] = auth_id
        self.__auth['logged_in'] = logged_in
        self.__auth['entity_id'] = entity_id
        self.__auth['email'] = email
        self.__auth['type'] = type
        self.__auth['device_name'] = device_name
        return self.insert(self.__auth)

    def logout_user(self, logged_out, action_type):
        self.__auth['logged_out'] = logged_out
        self.__auth['action_type'] = action_type
        self.__cursor.execute("""update authorizations set logged_out = %s, action_type = %s where auth_id = %s""", (self.__auth['logged_out'], self.__auth['action_type'], self.__id))
        self.__sql.commit()
        return True

    @staticmethod
    def get_active_tokens(email, type):
        sql = DBConnectivity.create_sql_connection()
        cursor = sql.cursor(dictionary=True)
        cursor.execute("""select * from authorizations where email = %s and logged_out = %s and type = %s""", (email, 0, type))
        res = cursor.fetchall()
        cursor.close()
        sql.close()
        return res

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.authorizations_create_table)
            # Inserting the record in the table
            self.__cursor.execute(
                """INSERT INTO authorizations (auth_id, email, type, entity_id, device_name, logged_in) VALUES (%s, %s, %s, %s, %s, %s)""",
                (values['auth_id'], values['email'], values['type'], values['entity_id'], values['device_name'], values['logged_in']))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='AuthorizationOps', function_name='insert()')
            log.log(error, priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='AuthorizationOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

# pprint(Authorization("kjabfadbshuerfasdvdasdf"))
# pprint(Authorization.get_active_tokens("anujpanchal@gmail.com", "b_user"))
# pprint(Authorization("kjabfadbshuervdasdf").logout_user(1596364744, "logout"))
# pprint(Authorization("").login_user("kjabfadbshuervdasdf", 1596361857, 1000, "anujpanchal@gmail.com", "chrome", "b_user"))
# pprint(Authorization.get_active_tokens("anujpanchal57@gmail.com"))