import traceback

import mysql.connector
from functionality import GenericOps, response
from functionality.Logger import Logger
from utility import DBConnectivity, conf, Implementations
from pprint import pprint
from exceptions import exceptions

class Supplier:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__supplier = {}
        if self.__id != "":
            self.__cursor.execute("""select * from suppliers where supplier_id = %s""", (self.__id, ))
            self.__supplier = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    # Adding a new supplier
    def add_supplier(self, company_name, activation_status=True, company_logo=""):
        self.__supplier['company_name'] = company_name
        self.__supplier['activation_status'] = activation_status
        self.__supplier['company_logo'] = company_logo
        timestamp = GenericOps.get_current_timestamp()
        self.__supplier['created_at'] = timestamp
        self.__supplier['updated_at'] = timestamp
        self.__supplier['supplier_id'] = self.insert(self.__supplier)
        return self.__supplier['supplier_id']

    def get_company_logo(self):
        return self.__supplier['company_logo']

    def get_company_name(self):
        return self.__supplier['company_name']

    def get_activation_status(self):
        return self.__supplier['activation_status']

    def get_profile_completed(self):
        return self.__supplier['profile_completed']

    def get_city(self):
        return self.__supplier['city']

    def get_business_address(self):
        return self.__supplier['business_address']

    def get_annual_revenue(self):
        return self.__supplier['annual_revenue']

    def get_industry(self):
        return self.__supplier['industry']

    def get_pincode(self):
        return self.__supplier['pincode']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.supplier_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO suppliers (company_name, company_logo, activation_status, created_at, updated_at) 
                                    VALUES (%s, %s, %s, %s, %s)""",
                                  (values['company_name'], values['company_logo'], values['activation_status'],
                                   values['created_at'], values['updated_at']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='SupplierOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def set_activation_status(self, status):
        self.__supplier['activation_status'] = 1 if status else 0
        self.__cursor.execute("update suppliers set activation_status = %s where supplier_id = %s", (status, self.__id))
        self.__sql.commit()
        return True

    def delete_supplier(self):
        try:
            self.__cursor.execute("""delete from suppliers where supplier_id = %s""", (self.__id, ))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierOps', function_name='delete_supplier()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException('Failed to delete supplier, please try again')
        except Exception as e:
            log = Logger(module_name='SupplierOps', function_name='delete_supplier()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException('Failed to delete supplier, please try again')

    def update_supplier_profile(self, annual_revenue, company_name, pan_no="", company_nature="", profile_completed=True):
        try:
            self.__supplier['annual_revenue'] = annual_revenue
            self.__supplier['company_name'] = company_name
            self.__supplier['pan_no'], self.__supplier['company_nature'] = pan_no, company_nature
            self.__supplier['profile_completed'] = 1 if profile_completed else 0
            self.__cursor.execute("""update suppliers set annual_revenue = %s, company_name = %s, 
                                    pan_no = %s, company_nature = %s, profile_completed = %s  where supplier_id = %s;""",
                                  (annual_revenue, company_name, pan_no, company_nature, profile_completed, self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierOps', function_name='update_supplier_profile()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException('Failed to update profile details, please try again')
        except Exception as e:
            log = Logger(module_name='SupplierOps', function_name='update_supplier_profile()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException('Failed to update profile details, please try again')

    def get_suppliers_count_on_profile_comp(self, buyer_id, profile_completed):
        try:
            self.__cursor.execute("""select count(*) as supplier_count
                                        from supplier_relationships as sr 
                                        join suppliers as s
                                        on sr.supplier_id = s.supplier_id
                                        join s_users as su
                                        on su.supplier_id = sr.supplier_id 
                                        where sr.buyer_id = %s and s.profile_completed = %s""", (buyer_id, profile_completed))
            res = self.__cursor.fetchone()['supplier_count']
            if res is None:
                res = 0
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierOps', function_name='get_suppliers_count_on_profile_comp()')
            log.log(str(error), priority='highest')
            return 0
        except Exception as e:
            log = Logger(module_name='SupplierOps', function_name='get_suppliers_count_on_profile_comp()')
            log.log(traceback.format_exc(), priority='highest')
            return 0

    def get_suppliers_for_po(self, requisition_id, status=True):
        try:
            self.__cursor.execute("""select s.supplier_id, s.company_name, s.profile_completed
                                    from suppliers as s
                                    join quotations as q
                                    on q.supplier_id = s.supplier_id
                                    where q.requisition_id = %s and q.status = %s""", (requisition_id, status))
            res = self.__cursor.fetchall()
            if res is None:
                return []
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierOps', function_name='get_suppliers_for_po()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='SupplierOps', function_name='get_suppliers_for_po()')
            log.log(traceback.format_exc(), priority='highest')
            return []

# pprint(Supplier().get_suppliers_count_on_profile_comp(1000, False))
# pprint(Supplier(1000).update_supplier_profile("Thane", "Mumbai, Thane", "10-15cr", "Engineering"))
# pprint(Supplier(1000))
# pprint(Supplier("").add_supplier("Bhavani"))
