import traceback
from pprint import pprint

import jwt
import mysql.connector
from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from exceptions import exceptions
from database.AuthorizationOps import Authorization

class BUser:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__buser = {}
        if self.__id != "":
            self.__cursor.execute("""select * from b_users where email = %s""", (self.__id,))
            self.__buser = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def get_busers_for_buyer_id(self, buyer_id):
        try:
            self.__cursor.execute("""select * from b_users where buyer_id = %s""", (buyer_id, ))
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='BuyerUserOps', function_name='get_busers_for_buyer_id()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='BuyerUserOps', function_name='get_busers_for_buyer_id()')
            log.log(traceback.format_exc(), priority='highest')
            return []

    # Adding a new user for a buyer company
    def add_buser(self, email, name, buyer_id, mobile_no, password, role, status=False):
        self.__buser['email'] = email
        self.__buser['name'] = name
        self.__buser['mobile_no'] = mobile_no
        self.__buser['buyer_id'] = buyer_id
        self.__buser['password'] = password
        self.__buser['role'] = role
        self.__buser['status'] = status
        timestamp = GenericOps.get_current_timestamp()
        self.__buser['created_at'] = timestamp
        self.__buser['updated_at'] = timestamp
        return self.insert(self.__buser)

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.buser_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO b_users (email, buyer_id, name, mobile_no, password, 
                        role, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['email'], values['buyer_id'], values['name'],
                                   values['mobile_no'], values['password'], values['role'], values['status'],
                                   values['created_at'], values['updated_at']))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='BuyerUserOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='BuyerUserOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    @staticmethod
    def is_buser(email, table="buser_table"):
        try:
            sql = DBConnectivity.create_sql_connection()
            cursor = sql.cursor(dictionary=True)
            cursor.execute("""SELECT * FROM information_schema.tables WHERE table_schema = %s AND table_name = %s LIMIT 1;""",
                           (conf.sqlconfig.get('database_name'), conf.sqlconfig.get('tables').get(table)))
            # Create a table if not exists
            if cursor.fetchone() is None:
                return False
            cursor.execute("""select * from b_users where email = %s""", (email, ))
            res = True if len(cursor.fetchall()) > 0 else False
            cursor.close()
            sql.close()
            return res

        except Exception as e:
            pprint(str(e))
            return False

    def get_buyer_id(self):
        return self.__buser['buyer_id']

    def get_status(self):
        return self.__buser['status']

    def get_email(self):
        return self.__buser['email']

    def get_name(self):
        return self.__buser['name']

    def get_first_name(self):
        return self.__buser['name'].split(" ")[0]

    def get_mobile_no(self):
        return self.__buser['mobile_no']

    def get_password(self):
        return self.__buser['password']

    def get_created_at(self):
        return self.__buser['created_at']

    def get_updated_at(self):
        return self.__buser['updated_at']

    # Encoding JWT token with an expiration time of 3 days
    def encode_auth_token(self):
        return (jwt.encode({"user": self.get_email(), "exp": GenericOps.get_current_timestamp() + conf.jwt_expiration}, conf.JWT_SECRET_KEY, algorithm="HS256")).decode('UTF-8')

    # Decoding a JWT token
    def decode_auth_token(self, token):
        try:
            decode = jwt.decode(token, conf.JWT_SECRET_KEY, algorithms=['HS256'])
            return decode
        except jwt.ExpiredSignatureError as e:
            return str(e)

    def is_admin(self):
        return True if self.__buser['role'].lower() == "admin" else False

    def set_password(self, password):
        self.__buser['password'] = password
        self.__cursor.execute("update b_users set password = %s where email = %s", (password, self.__id))
        self.__sql.commit()
        return True

    def set_status(self, status):
        self.__buser['status'] = status
        self.__cursor.execute("update b_users set status = %s where email = %s", (status, self.__id))
        self.__sql.commit()
        return True

# buser = BUser("anujpanchal57@gmail.com")
# pprint(BUser.is_buser("utkarsh.dhawan@exportify.in"))
# pprint(BUser("").add_buser("utkarsh.dhawan@exportify.in", "Utkarsh", 1000, "", "cbdbe4936ce8be63184d9f2e13fc249234371b9a", "admin"))
# pprint(buser.encode_auth_token())
# pprint(buser.decode_auth_toke())