import traceback

import mysql.connector
from functionality import GenericOps, response
from functionality.Logger import Logger
from utility import DBConnectivity, conf, Implementations
from pprint import pprint
from exceptions import exceptions

class SupplierBranches:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__supplier_branches = {}
        if self.__id != "":
            self.__cursor.execute("""select * from supplier_branches where branch_id = %s""", (self.__id, ))
            self.__supplier_branches = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_branches(self, supplier_id, business_address, city, pincode):
        self.__supplier_branches['supplier_id'] = supplier_id
        self.__supplier_branches['business_address'], self.__supplier_branches['city'], self.__supplier_branches['pincode'] = business_address, city, pincode
        self.__supplier_branches['branch_id'] = self.insert(self.__supplier_branches)
        return self.__supplier_branches['branch_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.supplier_branches_create_table)
            # Checking whether the record is added or not
            self.__cursor.execute("""select * from supplier_branches where supplier_id = %s""",
                                  (values['supplier_id'],))
            branch = self.__cursor.fetchall()
            if branch is None:
                is_branch_added = False
            else:
                is_branch_added = True if len(branch) > 0 else False
            # If the branch is present, then return True
            if is_branch_added:
                return True
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO supplier_branches (supplier_id, city, business_address, pincode) 
                                    VALUES (%s, %s, %s, %s)""",
                                  (values['supplier_id'], values['city'], values['business_address'],
                                   values['pincode']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierBranchesOps', function_name='insert()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add address details, please try again')

        except Exception as e:
            log = Logger(module_name='SupplierBranchesOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add address details, please try again')

    def insert_many(self, values):
        try:
            self.__cursor.execute(Implementations.supplier_branches_create_table)
            # Inserting the record in the table
            self.__cursor.executemany("""INSERT INTO supplier_branches (supplier_id, city, business_address, pincode) 
                                            VALUES (%s, %s, %s, %s)""", values)
            self.__sql.commit()
            last_row_id = self.__cursor.lastrowid
            result_ids = [last_row_id]
            for x in range(1, len(values)):
                result_ids.append(last_row_id + x)
            return result_ids

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierBranchesOps', function_name='insert_many()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add address details, please try again')

        except Exception as e:
            log = Logger(module_name='SupplierBranchesOps', function_name='insert_many()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add address details, please try again')

