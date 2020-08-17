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

    def get_suppliers_for_buyers(self, buyer_id):
        try:
            self.__cursor.execute("""select su.name, su.email, s.company_name, su.mobile_no, s.supplier_id
                                    from suppliers as s
                                    join s_users as su
                                    on s.supplier_id = su.supplier_id
                                    join supplier_relationships as sr
                                    on su.supplier_id = sr.supplier_id
                                    where sr.buyer_id = %s""", (buyer_id, ))
            res = self.__cursor.fetchall()
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='JoinOps', function_name='get_suppliers_for_buyers()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='JoinOps', function_name='get_suppliers_for_buyers()')
            log.log(traceback.format_exc(), priority='highest')
            return []

    def get_buyer_requisitions(self, buyer_id, start_limit, end_limit, req_type="open"):
        try:
            if req_type == "open":
                self.__cursor.execute("""select r.requisition_id, l.lot_name, r.deadline, r.timezone, r.currency, r.created_at, r.status, l.lot_id 
                                        from requisitions as r
                                        join lots as l
                                        on r.requisition_id = l.requisition_id
                                        where r.deadline > unix_timestamp() and buyer_id = %s
                                        order by r.created_at desc
                                        limit %s, %s;""", (buyer_id, start_limit, end_limit))
            # For time being, I have kept pending for approval and approved categories completely same
            elif req_type == "pending_approval":
                self.__cursor.execute("""select r.requisition_id, l.lot_name, r.deadline, r.timezone, r.currency, r.created_at, r.status, l.lot_id
                                        from requisitions as r
                                        join lots as l
                                        on r.requisition_id = l.requisition_id
                                        where r.deadline < unix_timestamp() and buyer_id = %s
                                        order by r.created_at desc
                                        limit %s, %s;""", (buyer_id, start_limit, end_limit))
            elif req_type == "approved":
                self.__cursor.execute("""select r.requisition_id, l.lot_name, r.deadline, r.timezone, r.currency, r.created_at, r.status, l.lot_id
                                        from requisitions as r
                                        join lots as l
                                        on r.requisition_id = l.requisition_id
                                        where r.deadline < unix_timestamp() and buyer_id = %s
                                        order by r.created_at desc
                                        limit %s, %s;""", (buyer_id, start_limit, end_limit))
            else:
                self.__cursor.execute("""select r.requisition_id, l.lot_name, r.deadline, r.timezone, r.currency, r.created_at, r.status, l.lot_id
                                        from requisitions as r
                                        join lots as l
                                        on r.requisition_id = l.requisition_id
                                        where r.cancelled = true and buyer_id = %s
                                        order by r.created_at desc
                                        limit %s, %s;""", (buyer_id, start_limit, end_limit))
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

# pprint(Join().get_suppliers_info(1000))
# pprint(Join().get_invited_suppliers(1000))
# pprint(Join().get_buyers_for_rfq(1000))
# pprint(Join().get_suppliers_quoting(1000, "rfq"))
# pprint(Join().get_buyer_requisitions(1000, 0, 5, "open"))