import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector

class Buyer:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__buyer = {}
        if self.__id != "":
            self.__cursor.execute("""select * from buyers where buyer_id = %s""", (self.__id, ))
            self.__buyer = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    # Adding a new buyer
    def add_buyer(self, company_name, domain_name, auto_join=True, default_currency="inr", subscription_plan="", activation_status=False, company_logo=""):
        self.__buyer['company_name'] = company_name
        self.__buyer['domain_name'] = domain_name
        self.__buyer['activation_status'] = activation_status
        self.__buyer['subscription_plan'] = subscription_plan
        self.__buyer['company_logo'] = company_logo
        self.__buyer['default_currency'] = default_currency
        self.__buyer['auto_join'] = auto_join
        timestamp = GenericOps.get_current_timestamp()
        self.__buyer['created_at'] = timestamp
        self.__buyer['updated_at'] = timestamp
        self.__buyer['buyer_id'] = self.insert(self.__buyer)
        return self.__buyer['buyer_id']

    def insert(self, values, table="buyer_table"):
        try:
            # Checking whether the table exists or not
            self.__cursor.execute(Implementations.buyer_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO buyers (company_name, auto_join, domain_name, company_logo, default_currency, 
                        subscription_plan, activation_status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['company_name'], values['auto_join'], values['domain_name'],
                                   values['company_logo'], values['default_currency'], values['subscription_plan'], values['activation_status'],
                                   values['created_at'], values['updated_at']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='BuyerOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='BuyerOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    @staticmethod
    def is_buyer_domain_registered(email, table="buyer_table"):
        company_domain = email.split('@')[1]
        sql = DBConnectivity.create_sql_connection()
        cursor = sql.cursor(dictionary=True)
        cursor.execute(
            """SELECT * FROM information_schema.tables WHERE table_schema = %s AND table_name = %s LIMIT 1;""",
            (conf.sqlconfig.get('database_name'), conf.sqlconfig.get('tables').get(table)))
        # Create a table if not exists
        if cursor.fetchone() is None:
            return False
        cursor.execute("""select * from buyers where domain_name=%s;""", (company_domain, ))
        res = cursor.fetchone()
        cursor.close()
        sql.close()
        return res

    def update_activation_status(self, status):
        self.__buyer['activation_status'] = status
        self.__cursor.execute("update buyers set activation_status = %s where buyer_id = %s", (status, self.__id))
        self.__sql.commit()
        return True

    def get_activation_status(self):
        return self.__buyer['activation_status']

    def get_subscription_plan(self):
        return self.__buyer['subscription_plan']

    def get_auto_join(self):
        return self.__buyer['auto_join']

    def get_default_currency(self):
        return self.__buyer['default_currency']

    def get_company_logo(self):
        return self.__buyer['company_logo']

    def get_company_name(self):
        return self.__buyer['company_name']

# pprint(Buyer(1000))
# pprint(Buyer("").add_buyer("Bhavani", "gmail.com"))
# pprint(Buyer.is_buyer_domain_registered("anuj.panchal@exportify.in"))
# pprint(Buyer(1000).set_auto_join(False))
# pprint(Buyer(1007).update_activation_status(True))