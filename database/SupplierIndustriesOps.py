import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class SupplierIndustries:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__supplier_industries = {}
        if self.__id != "":
            self.__cursor.execute("""select * from supplier_industries where mapper_id = %s""", (self.__id, ))
            self.__supplier_industries = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_supplier_industries(self, supplier_id, industry_id):
        self.__supplier_industries['supplier_id'], self.__supplier_industries['industry_id'] = supplier_id, industry_id
        self.__supplier_industries['mapper_id'] = self.insert(self.__supplier_industries)
        return self.__supplier_industries['mapper_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.supplier_industries_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO supplier_industries (supplier_id, industry_id) VALUES (%s, %s)""",
                                  (values['supplier_id'], values['industry_id']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierIndustriesOps', function_name='insert()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add supplier industries, please try again')
        except Exception as e:
            log = Logger(module_name='SupplierIndustriesOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add supplier industries, please try again')

    def insert_many(self, values):
        try:
            self.__cursor.execute(Implementations.supplier_industries_create_table)
            # Inserting the record in the table
            self.__cursor.executemany("""INSERT INTO supplier_industries (supplier_id, industry_id) VALUES (%s, %s)""", values)
            self.__sql.commit()
            last_row_id = self.__cursor.lastrowid
            result_ids = [last_row_id]
            for x in range(1, len(values)):
                result_ids.append(last_row_id + x)
            return result_ids

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierIndustriesOps', function_name='insert_many()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add supplier industries, please try again')
        except Exception as e:
            log = Logger(module_name='SupplierIndustriesOps', function_name='insert_many()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add supplier industries, please try again')