import traceback
from pprint import pprint
import jwt
import mysql.connector
from functionality import GenericOps, response
from functionality.Logger import Logger
from utility import DBConnectivity, conf, Implementations
from exceptions import exceptions
from database.AuthorizationOps import Authorization

class Join:
    def __init__(self):
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def get_suppliers_info(self, buyer_id):
        try:
            self.__cursor.execute("""select su.name, su.mobile_no, su.email, s.company_name 
                                    from supplier_relationships as sr join suppliers as s
                                    on sr.supplier_id = s.supplier_id
                                    join s_users as su
                                    on su.supplier_id = sr.supplier_id where sr.buyer_id = %s""", (buyer_id, ))
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='JoinOps', function_name='get_suppliers_info()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='JoinOps', function_name='get_suppliers_info()')
            log.log(traceback.format_exc(), priority='highest')
            return []

    def get_invited_suppliers(self, operation_id, operation_type="rfq"):
        try:
            self.__cursor.execute("""select substring_index(su.name, " ", 1) as name, su.email, s.company_name, su.mobile_no
                                    from suppliers as s 
                                    join s_users as su
                                    on s.supplier_id = su.supplier_id
                                    join invited_suppliers as ins
                                    on su.supplier_id = ins.supplier_id
                                    where operation_type = %s and operation_id = %s""", (operation_type, operation_id))
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='JoinOps', function_name='get_invited_suppliers()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='JoinOps', function_name='get_invited_suppliers()')
            log.log(traceback.format_exc(), priority='highest')
            return []

    def get_buyers_for_rfq(self, requisition_id):
        try:
            self.__cursor.execute("""select substring_index(bu.name, " ", 1) as name, bu.email, r.requisition_name 
                                    from b_users as bu
                                    join buyers as b
                                    on bu.buyer_id = b.buyer_id
                                    join requisitions as r
                                    on b.buyer_id = r.buyer_id
                                    where requisition_id = %s""", (requisition_id, ))
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='JoinOps', function_name='get_buyers_for_rfq()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='JoinOps', function_name='get_buyers_for_rfq()')
            log.log(traceback.format_exc(), priority='highest')
            return []

    def get_suppliers_quoting(self, operation_id, operation_type):
        try:
            self.__cursor.execute("""select s.supplier_id, s.company_name, su.name, su.email, su.mobile_no, ins.unlock_status
                                    from suppliers as s
                                    join s_users as su
                                    on s.supplier_id = su.supplier_id
                                    join invited_suppliers as ins
                                    on su.supplier_id = ins.supplier_id
                                    where operation_id = %s and operation_type = %s""", (operation_id, operation_type))
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='JoinOps', function_name='get_suppliers_quoting()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='JoinOps', function_name='get_suppliers_quoting()')
            log.log(traceback.format_exc(), priority='highest')
            return []

# pprint(Join().get_suppliers_info(1000))
# pprint(Join().get_invited_suppliers(1000))
# pprint(Join().get_buyers_for_rfq(1000))
# pprint(Join().get_suppliers_quoting(1000, "rfq"))