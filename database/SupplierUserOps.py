import traceback
from pprint import pprint
import jwt
import mysql.connector
from functionality import GenericOps, response
from functionality.Logger import Logger
from utility import DBConnectivity, conf, Implementations
from exceptions import exceptions
from database.AuthorizationOps import Authorization

class SUser:
    def __init__(self, _id="", supplier_id=""):
        self.__id = _id
        self.__supplier_id = supplier_id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__suser = {}
        if self.__id != "":
            self.__cursor.execute("""select * from s_users where email = %s""", (self.__id, ))
            self.__suser = self.__cursor.fetchone()
        if self.__supplier_id != "":
            self.__cursor.execute("select * from s_users where supplier_id = %s", (self.__supplier_id, ))
            self.__suser = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    # Adding a new user for a buyer company
    def add_suser(self, email, name, supplier_id, password, mobile_no="", role="admin", status=True):
        self.__suser['email'] = email
        self.__suser['name'] = name
        self.__suser['mobile_no'] = mobile_no
        self.__suser['supplier_id'] = supplier_id
        self.__suser['password'] = password
        self.__suser['role'] = role
        self.__suser['status'] = status
        timestamp = GenericOps.get_current_timestamp()
        self.__suser['created_at'] = timestamp
        self.__suser['updated_at'] = timestamp
        return self.insert(self.__suser)

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.suser_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO s_users (email, supplier_id, name, mobile_no, password, 
                        role, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['email'], values['supplier_id'], values['name'],
                                   values['mobile_no'], values['password'], values['role'],
                                   values['status'], values['created_at'], values['updated_at']))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierUserOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='SupplierUserOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def delete_suser(self, supplier_id):
        try:
            self.__cursor.execute("""delete from s_users where supplier_id = %s""", (supplier_id, ))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierUserOps', function_name='delete_suser()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException('Failed to delete supplier, please try again')
        except Exception as e:
            log = Logger(module_name='SupplierUserOps', function_name='delete_suser()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException('Failed to delete supplier, please try again')

    @staticmethod
    def is_suser(email, table="suser_table"):
        sql = DBConnectivity.create_sql_connection()
        cursor = sql.cursor(dictionary=True)
        cursor.execute("""SELECT * FROM information_schema.tables WHERE table_schema = %s AND table_name = %s LIMIT 1;""",
                       (conf.sqlconfig.get('database_name'), conf.sqlconfig.get('tables').get(table)))
        if cursor.fetchone() is None:
            return False
        cursor.execute("""select * from s_users where email = %s""", (email,))
        res = True if len(cursor.fetchall()) > 0 else False
        cursor.close()
        sql.close()
        return res

    def get_suser(self):
        return self.__suser

    def get_name(self):
        return self.__suser['name']

    def get_first_name(self):
        return self.__suser['name'].split(" ")[0]

    def get_mobile_no(self):
        return self.__suser['mobile_no']

    def get_buyer_id(self):
        return self.__suser['buyer_id']

    def get_password(self):
        return self.__suser['password']

    def get_role(self):
        return self.__suser['role']

    def get_status(self):
        return self.__suser['status']

    def get_created_at(self):
        return self.__suser['created_at']

    def get_updated_at(self):
        return self.__suser['updated_at']

    def set_password(self, password):
        try:
            self.__suser['password'] = password
            self.__cursor.execute("update s_users set password = %s where email = %s", (password, self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierUserOps', function_name='set_password()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException('Failed to update password, please try again')
        except Exception as e:
            log = Logger(module_name='SupplierUserOps', function_name='set_password()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException('Failed to update password, please try again')

    def update_suser_details(self, name, mobile_no):
        try:
            self.__suser['name'], self.__suser['mobile_no'] = name, mobile_no
            self.__cursor.execute("update s_users set name = %s, mobile_no = %s where email = %s", (name, mobile_no, self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierUserOps', function_name='update_suser_details()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException('Failed to update user details, please try again')
        except Exception as e:
            log = Logger(module_name='SupplierUserOps', function_name='update_suser_details()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException('Failed to update user details, please try again')

    def get_supplier_id(self):
        return self.__suser['supplier_id']

    def get_email(self):
        return self.__suser['email']

    def set_status(self, status):
        self.__suser['status'] = status
        self.__cursor.execute("update s_users set status = %s where email = %s", (status, self.__id))
        self.__sql.commit()
        return True

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

# suser = SUser("anujpanchal57@gmail.com")
# pprint(SUser("").add_suser("avinash.kothari@exportify.in", "Avinash", 1000, "cbdbe4936ce8be63184d9f2e13fc249234371b9a"))
# pprint(SUser.is_suser("avinash.kothari@exportify.in"))
# pprint(suser.encode_auth_token())
# pprint(suser.decode_auth_toke())