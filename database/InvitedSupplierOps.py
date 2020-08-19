import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class InviteSupplier:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__inv_supplier = {}
        if self.__id != "":
            self.__cursor.execute("""select * from invited_suppliers where invite_id = %s""", (self.__id, ))
            self.__inv_supplier = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_supplier(self, operation_id, operation_type, supplier_id, unlock_status=True):
        self.__inv_supplier['operation_id'] = operation_id
        self.__inv_supplier['operation_type'] = operation_type
        self.__inv_supplier['supplier_id'] = supplier_id
        self.__inv_supplier['invited_on'] = GenericOps.get_current_timestamp()
        self.__inv_supplier['unlock_status'] = unlock_status
        self.__inv_supplier['invite_id'] = self.insert(self.__inv_supplier)
        return self.__inv_supplier['invite_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.invited_suppliers_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO invited_suppliers (operation_id, operation_type, supplier_id, invited_on, unlock_status) 
            VALUES (%s, %s, %s, %s, %s)""",
                                  (values['operation_id'], values['operation_type'],
                                   values['supplier_id'], values['invited_on'],
                                   values['unlock_status']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='InvitedSupplierOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='InvitedSupplierOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def insert_many(self, values):
        try:
            self.__cursor.execute(Implementations.invited_suppliers_create_table)
            # Inserting the record in the table
            self.__cursor.executemany("""INSERT INTO invited_suppliers (operation_id, operation_type, supplier_id, invited_on, unlock_status) 
            VALUES (%s, %s, %s, %s, %s)""", values)
            self.__sql.commit()
            last_row_id = self.__cursor.lastrowid
            result_ids = [last_row_id]
            for x in range(1, len(values)):
                result_ids.append(last_row_id + x)
            return result_ids

        except mysql.connector.Error as error:
            log = Logger(module_name='InvitedSupplierOps', function_name='insert_many()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to invite supplier, please try again')
        except Exception as e:
            log = Logger(module_name='InvitedSupplierOps', function_name='insert_many()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to invite supplier, please try again')

    def update_unlock_status(self, supplier_id, operation_id, operation_type, status):
        try:
            self.__inv_supplier['unlock_status'] = status
            self.__cursor.execute("update invited_suppliers set unlock_status = %s where operation_id = %s and operation_type = %s and supplier_id = %s",
                                  (status, operation_id, operation_type, supplier_id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='InvitedSupplierOps', function_name='update_unlock_status()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to update unlock status of a supplier, please try again')
        except Exception as e:
            log = Logger(module_name='InvitedSupplierOps', function_name='update_unlock_status()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to update unlock status of a supplier, please try again')

    def get_unlock_status(self, supplier_id, operation_id, operation_type):
        self.__cursor.execute("""select unlock_status from invited_suppliers where supplier_id = %s and operation_id = %s and operation_type = %s""",
                              (supplier_id, operation_id, operation_type))
        res = self.__cursor.fetchone()
        self.__sql.commit()
        return res['unlock_status']

    def remove_supplier(self, supplier_id, operation_id, operation_type):
        try:
            self.__cursor.execute("""delete from invited_suppliers where supplier_id = %s and operation_id = %s and operation_type = %s""",
                                  (supplier_id, operation_id, operation_type))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='InvitedSupplierOps', function_name='remove_supplier()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to remove supplier, please try again')
        except Exception as e:
            log = Logger(module_name='InvitedSupplierOps', function_name='remove_supplier()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to remove supplier, please try again')

    def get_operation_suppliers_count(self, operation_id, operation_type):
        try:
            self.__cursor.execute("""select count(*) as ins_count from invited_suppliers
                                    where operation_id = %s and operation_type = %s;""",
                                  (operation_id, operation_type))
            res = self.__cursor.fetchall()
            return res[0]['ins_count']

        except mysql.connector.Error as error:
            log = Logger(module_name='InvitedSupplierOps', function_name='get_operation_suppliers()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='InvitedSupplierOps', function_name='get_operation_suppliers()')
            log.log(traceback.format_exc(), priority='highest')
            return False


# pprint(InviteSupplier().add_supplier(1000, "auction", 1000))
# pprint(InviteSupplier().get_unlock_status(1000, 1000, "rfq"))
# pprint(InviteSupplier().get_operation_suppliers_count(1000, "rfq"))