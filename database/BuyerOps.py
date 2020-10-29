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
        cursor.execute("""select * from buyers where domain_name = %s;""", (company_domain, ))
        res = cursor.fetchone()
        cursor.close()
        sql.close()
        return res

    def update_activation_status(self, status):
        self.__buyer['activation_status'] = status
        self.__cursor.execute("update buyers set activation_status = %s where buyer_id = %s", (status, self.__id))
        self.__sql.commit()
        return True

    def update_po_incr_factor(self, po_incr_factor):
        self.__buyer['po_incr_factor'] = po_incr_factor
        self.__cursor.execute("update buyers set po_incr_factor = %s where buyer_id = %s", (po_incr_factor, self.__id))
        self.__sql.commit()
        return True

    def update_po_suffix(self, po_suffix):
        self.__buyer['po_suffix'] = po_suffix
        self.__cursor.execute("update buyers set po_suffix = %s where buyer_id = %s", (po_suffix, self.__id))
        self.__sql.commit()
        return True

    def update_gst_no(self, gst_no):
        self.__buyer['gst_no'] = gst_no
        self.__cursor.execute("update buyers set gst_no = %s where buyer_id = %s", (gst_no, self.__id))
        self.__sql.commit()
        return True

    def update_business_address(self, business_address):
        self.__buyer['business_address'] = business_address
        self.__cursor.execute("update buyers set business_address = %s where buyer_id = %s", (business_address, self.__id))
        self.__sql.commit()
        return True

    def update_pincode(self, pincode):
        self.__buyer['pincode'] = pincode
        self.__cursor.execute("update buyers set pincode = %s where buyer_id = %s", (pincode, self.__id))
        self.__sql.commit()
        return True

    def update_country(self, country):
        self.__buyer['country'] = country
        self.__cursor.execute("update buyers set country = %s where buyer_id = %s", (country, self.__id))
        self.__sql.commit()
        return True

    def update_cin(self, cin):
        self.__buyer['cin'] = cin
        self.__cursor.execute("update buyers set cin = %s where buyer_id = %s", (cin, self.__id))
        self.__sql.commit()
        return True

    def update_company_email_address(self, company_email_address):
        self.__buyer['company_email_address'] = company_email_address
        self.__cursor.execute("update buyers set company_email_address = %s where buyer_id = %s", (company_email_address, self.__id))
        self.__sql.commit()
        return True

    def update_company_contact_number(self, company_contact_number):
        self.__buyer['company_contact_number'] = company_contact_number
        self.__cursor.execute("update buyers set company_contact_number = %s where buyer_id = %s", (company_contact_number, self.__id))
        self.__sql.commit()
        return True

    def update_default_po_additional_note_id(self, template_id):
        self.__buyer['default_po_additional_note_id'] = template_id
        self.__cursor.execute("update buyers set default_po_additional_note_id = %s where buyer_id = %s", (template_id, self.__id))
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

    def get_city(self):
        return self.__buyer['city']

    def get_business_address(self):
        return self.__buyer['business_address']

    def get_pincode(self):
        return self.__buyer['pincode']

    def get_gst_no(self):
        return self.__buyer['gst_no']

    def get_filing_frequency(self):
        return self.__buyer['filing_frequency']

    def get_gst_status(self):
        return self.__buyer['gst_status']

    def get_country(self):
        return self.__buyer['country']

    def get_po_incr_factor(self):
        return self.__buyer['po_incr_factor']

    def get_po_suffix(self):
        return self.__buyer['po_suffix']

    def get_cin(self):
        return self.__buyer['cin']

    def get_company_contact_number(self):
        return self.__buyer['company_contact_number']

    def get_company_email_address(self):
        return self.__buyer['company_email_address']

    def get_default_po_additional_note_id(self):
        return self.__buyer['default_po_additional_note_id']

    def search_suppliers(self, search_str, category="all", supplier_category="all"):
        try:
            if supplier_category == "all":
                if category == "all":
                    self.__cursor.execute("select su.name, su.mobile_no, su.email, s.company_name, s.supplier_id, s.profile_completed, sr.supplier_category from supplier_relationships as sr join suppliers as s on sr.supplier_id = s.supplier_id join s_users as su on su.supplier_id = sr.supplier_id where sr.buyer_id = " + str(self.__id) + " and (lower(s.company_name) like '%" + search_str + "%' or lower(su.name) like '%" + search_str + "%' or lower(su.email) like '%" + search_str + "%' or su.mobile_no like '%" + search_str + "%') order by su.created_at desc")
                else:
                    profile_completed = True if category == "onboarded" else False
                    self.__cursor.execute("select su.name, su.mobile_no, su.email, s.company_name, s.supplier_id, s.profile_completed, sr.supplier_category from supplier_relationships as sr join suppliers as s on sr.supplier_id = s.supplier_id join s_users as su on su.supplier_id = sr.supplier_id where sr.buyer_id = " + str(self.__id) + " and s.profile_completed = " + str(profile_completed) + " and (lower(s.company_name) like '%" + search_str + "%' or lower(su.name) like '%" + search_str + "%' or lower(su.email) like '%" + search_str + "%' or su.mobile_no like '%" + search_str + "%') order by su.created_at desc")
            else:
                if category == "all":
                    self.__cursor.execute(
                        "select su.name, su.mobile_no, su.email, s.company_name, s.supplier_id, s.profile_completed, sr.supplier_category from supplier_relationships as sr join suppliers as s on sr.supplier_id = s.supplier_id join s_users as su on su.supplier_id = sr.supplier_id where sr.buyer_id = " + str(
                            self.__id) + " and lower(sr.supplier_category) = '" + supplier_category + "' and (lower(s.company_name) like '%" + search_str + "%' or lower(su.name) like '%" + search_str + "%' or lower(su.email) like '%" + search_str + "%' or su.mobile_no like '%" + search_str + "%') order by su.created_at desc")
                else:
                    profile_completed = True if category == "onboarded" else False
                    self.__cursor.execute(
                        "select su.name, su.mobile_no, su.email, s.company_name, s.supplier_id, s.profile_completed, sr.supplier_category from supplier_relationships as sr join suppliers as s on sr.supplier_id = s.supplier_id join s_users as su on su.supplier_id = sr.supplier_id where sr.buyer_id = " + str(
                            self.__id) + " and s.profile_completed = " + str(
                            profile_completed) + " and lower(sr.supplier_category) = '" + supplier_category + "' and (lower(s.company_name) like '%" + search_str + "%' or lower(su.name) like '%" + search_str + "%' or lower(su.email) like '%" + search_str + "%' or su.mobile_no like '%" + search_str + "%') order by su.created_at desc")
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='BuyerOps', function_name='search_suppliers()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='BuyerOps', function_name='search_suppliers()')
            log.log(traceback.format_exc(), priority='highest')
            return []

# pprint(Buyer(1000))
# pprint(Buyer(1000).search_suppliers(search_str="s", category="all", supplier_category="all"))
# pprint(Buyer("").add_buyer("Bhavani", "gmail.com"))
# pprint(Buyer.is_buyer_domain_registered("anuj.panchal@exportify.in"))
# pprint(Buyer(1000).set_auto_join(False))
# pprint(Buyer(1007).update_activation_status(True))