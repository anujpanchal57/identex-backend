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
            self.__cursor.execute("""select * from b_users where _id = %s""", (self.__id,))
            self.__buser = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    # Adding a new user for a buyer company
    def add_buser(self, email, name, buyer_id, mobile_no, password, role, status=False):
        self.__buser['_id'] = email
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
            self.__cursor.execute("""INSERT INTO b_users (_id, buyer_id, name, mobile_no, password, 
                        role, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['_id'], values['buyer_id'], values['name'],
                                   values['mobile_no'], values['password'], values['role'], values['status'],
                                   values['created_at'], values['updated_at']))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='BuyerUserOps', function_name='insert()')
            log.log(error, priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='BuyerUserOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    @staticmethod
    def is_buser(email, table="buser_table"):
        sql = DBConnectivity.create_sql_connection()
        cursor = sql.cursor(dictionary=True)
        cursor.execute("""SELECT * FROM information_schema.tables WHERE table_schema = %s AND table_name = %s LIMIT 1;""",
                       (conf.sqlconfig.get('database_name'), conf.sqlconfig.get('tables').get(table)))
        # Create a table if not exists
        if cursor.fetchone() is None:
            return False
        cursor.execute("""select _id from b_users where _id = %s""", (email, ))
        res = True if len(cursor.fetchall()) > 0 else False
        cursor.close()
        sql.close()
        return res

    def get_buyer_id(self):
        return self.__buser['buyer_id']

    def get_status(self):
        return self.__buser['status']

    def get_email(self):
        return self.__buser['_id']

    def get_name(self):
        return self.__buser['name']

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
        self.__cursor.execute("update b_users set password = %s where _id = %s", (password, self.__id))
        self.__sql.commit()
        return True

    def set_status(self, status):
        self.__buser['status'] = status
        self.__cursor.execute("update b_users set status = %s where _id = %s", (status, self.__id))
        self.__sql.commit()
        return True

# buser = BUser("anujpanchal57@gmail.com")
# pprint(BUser.is_buser("anuj.panchal@exportify.in"))
# pprint(BUser("").add_buser("utkarsh.dhawan@exportify.in", "Utkarsh", 1000, "", "cbdbe4936ce8be63184d9f2e13fc249234371b9a", "admin"))
# pprint(buser.encode_auth_token())
# pprint(buser.decode_auth_toke())