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
    def add_supplier(self, company_name, activation_status=True, company_logo="", city="", business_address="",
                     annual_revenue="", industry=""):
        self.__supplier['company_name'] = company_name
        self.__supplier['activation_status'] = activation_status
        self.__supplier['company_logo'] = company_logo
        timestamp = GenericOps.get_current_timestamp()
        self.__supplier['created_at'] = timestamp
        self.__supplier['updated_at'] = timestamp
        self.__supplier['city'] = city
        self.__supplier['business_address'] = business_address
        self.__supplier['annual_revenue'] = annual_revenue
        self.__supplier['industry'] = industry
        self.__supplier['supplier_id'] = self.insert(self.__supplier)
        return self.__supplier['supplier_id']

    def get_company_logo(self):
        return self.__supplier['company_logo']

    def get_company_name(self):
        return self.__supplier['company_name']

    def get_activation_status(self):
        return self.__supplier['activation_status']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.supplier_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO suppliers (company_name, company_logo, activation_status, created_at, updated_at, 
                                    city, business_address, annual_revenue, industry) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['company_name'], values['company_logo'], values['activation_status'],
                                   values['created_at'], values['updated_at'], values['city'], values['business_address'],
                                   values['annual_revenue'], values['industry']))
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

    def update_supplier_profile(self, city, business_address, annual_revenue, industry):
        try:
            self.__cursor.execute("""update suppliers set city = %s, business_address = %s, annual_revenue = %s, industry = %s 
                                    where supplier_id = %s;""", (city, business_address, annual_revenue, industry, self.__id))
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


# pprint(Supplier(1000).update_supplier_profile("Thane", "Mumbai, Thane", "10-15cr", "Engineering"))
# pprint(Supplier(1000))
# pprint(Supplier("").add_supplier("Bhavani"))
