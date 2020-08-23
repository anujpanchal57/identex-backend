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
            self.__cursor.execute("""select su.name, su.mobile_no, su.email, s.company_name, s.supplier_id
                                    from supplier_relationships as sr 
                                    join suppliers as s
                                    on sr.supplier_id = s.supplier_id
                                    join s_users as su
                                    on su.supplier_id = sr.supplier_id 
                                    where sr.buyer_id = %s
                                    order by su.created_at desc""", (buyer_id, ))
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

    # Made this method for the sake of email
    def get_invited_suppliers(self, operation_id, operation_type="rfq"):
        try:
            self.__cursor.execute("""select substring_index(su.name, " ", 1) as name, su.email, s.company_name, su.mobile_no
                                    from suppliers as s 
                                    join s_users as su
                                    on s.supplier_id = su.supplier_id
                                    join invited_suppliers as ins
                                    on su.supplier_id = ins.supplier_id
                                    where ins.operation_type = %s and ins.operation_id = %s 
                                    order by ins.invited_on desc;""", (operation_type, operation_id))
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

    def get_suppliers_messaging(self, operation_id, operation_type):
        try:
            self.__cursor.execute("""select s.supplier_id, s.company_name, su.name, su.email
                                    from suppliers as s
                                    join s_users as su
                                    on s.supplier_id = su.supplier_id
                                    join invited_suppliers as ins
                                    on su.supplier_id = ins.supplier_id
                                    where operation_id = %s and operation_type = %s""", (operation_id, operation_type))
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='JoinOps', function_name='get_suppliers_messaging()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='JoinOps', function_name='get_suppliers_messaging()')
            log.log(traceback.format_exc(), priority='highest')
            return []

    def get_buyer_requisitions(self, buyer_id, start_limit, end_limit, cancelled, req_type="open"):
        try:
            self.__cursor.execute("""select r.requisition_id, l.lot_name, r.deadline, r.timezone, r.currency, r.created_at, r.status, l.lot_id 
                                    from requisitions as r
                                    join lots as l
                                    on r.requisition_id = l.requisition_id
                                    where r.request_type = %s and buyer_id = %s and r.cancelled = %s
                                    order by r.created_at desc
                                    limit %s, %s;""", (req_type, buyer_id, cancelled,start_limit, end_limit))
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='JoinOps', function_name='get_buyer_requisitions()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='JoinOps', function_name='get_buyer_requisitions()')
            log.log(traceback.format_exc(), priority='highest')
            return []

    def get_supplier_requisitions(self, supplier_id, start_limit, end_limit, cancelled, req_type="open", operation_type="rfq"):
        try:
            self.__cursor.execute("""select r.requisition_id, l.lot_id, l.lot_name, l.lot_description, r.deadline, r.currency, r.timezone, b.company_name as buyer_company_name, 
                                    b.buyer_id, r.supplier_instructions, r.tnc, ins.unlock_status
                                    from invited_suppliers as ins 
                                    join requisitions as r
                                    on ins.operation_id = r.requisition_id
                                    join lots as l
                                    on r.requisition_id = l.requisition_id
                                    join buyers as b
                                    on r.buyer_id = b.buyer_id
                                    where r.request_type = %s and ins.supplier_id = %s and ins.operation_type = %s
                                    and r.cancelled = %s
                                    order by r.created_at desc
                                    limit %s, %s;""", (req_type, supplier_id, operation_type, cancelled, start_limit, end_limit))
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='JoinOps', function_name='get_supplier_requisitions()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='JoinOps', function_name='get_supplier_requisitions()')
            log.log(traceback.format_exc(), priority='highest')
            return []

    def get_buyer_requisitions_count(self, buyer_id, req_type="open"):
        try:
            self.__cursor.execute("""select count(*) as requisition_count
                                    from requisitions
                                    where request_type = %s and buyer_id = %s;""", (req_type, buyer_id))
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='JoinOps', function_name='get_buyer_requisitions_count()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='JoinOps', function_name='get_buyer_requisitions_count()')
            log.log(traceback.format_exc(), priority='highest')
            return []

    def get_supplier_requisitions_count(self, supplier_id, req_type="open", operation_type="rfq"):
        try:
            self.__cursor.execute("""select count(*) as requisitions_count
                                    from invited_suppliers as ins 
                                    join requisitions as r
                                    on ins.operation_id = r.requisition_id
                                    where r.request_type = %s and ins.supplier_id = %s and ins.operation_type = %s""",
                                  (req_type, supplier_id, operation_type))
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='JoinOps', function_name='get_supplier_requisitions_count()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='JoinOps', function_name='get_supplier_requisitions_count()')
            log.log(traceback.format_exc(), priority='highest')
            return []


# pprint(Join().get_supplier_requisitions_count(supplier_id=1000))
# pprint(Join().get_buyer_requisitions_count(buyer_id=1000, req_type="cancelled"))
# pprint(Join().get_suppliers_for_buyers(1000))
# pprint(Join().get_suppliers_info(1000))
# pprint(Join().get_invited_suppliers(1000))
# pprint(Join().get_buyers_for_rfq(1000))
# pprint(Join().get_suppliers_quoting(1000, "rfq"))
# pprint(Join().get_buyer_requisitions(1000, 0, 5, "open"))
# pprint(Join().get_supplier_requisitions(1001, 0, 5))