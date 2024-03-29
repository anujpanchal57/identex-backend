import traceback
from pprint import pprint
import mysql.connector
from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from exceptions import exceptions

class SupplierRelationship:
    def __init__(self, _id="", type="buyer"):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__s_relations = {}
        if self.__id != "" and type == "buyer":
            self.__cursor.execute("""select supplier_id from supplier_relationships where buyer_id = %s""", (self.__id,))
            self.__s_relations = self.__cursor.fetchall()
        if self.__id != "" and type == "supplier":
            self.__cursor.execute("""select buyer_id from supplier_relationships where supplier_id = %s""", (self.__id,))
            self.__s_relations = self.__cursor.fetchall()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def get_buyer_suppliers(self):
        return self.__s_relations

    def add_supplier_relationship(self, buyer_id, supplier_id, supplier_category="uncategorized"):
        self.__s_relations['supplier_id'] = supplier_id
        self.__s_relations['buyer_id'] = buyer_id
        self.__s_relations['supplier_category'] = supplier_category
        return self.insert(self.__s_relations)

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.supplier_relationship_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO supplier_relationships (buyer_id, supplier_id, supplier_category) VALUES (%s, %s, %s)""",
                                  (values['buyer_id'], values['supplier_id'], values['supplier_category']))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierRelationshipOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='SupplierRelationshipOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def delete_supplier_relationship(self, buyer_id, supplier_id):
        try:
            self.__cursor.execute("""delete from supplier_relationships where buyer_id = %s and supplier_id = %s""",
                                  (buyer_id, supplier_id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierRelationshipOps', function_name='delete_supplier_relationship()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException('Failed to delete supplier, please try again')
        except Exception as e:
            log = Logger(module_name='SupplierRelationshipOps', function_name='delete_supplier_relationship()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException('Failed to delete supplier, please try again')

    def update_supplier_category(self, buyer_id, supplier_id, category):
        try:
            self.__cursor.execute("""update supplier_relationships set supplier_category = %s where buyer_id = %s and supplier_id = %s""",
                                  (category, buyer_id, supplier_id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierRelationshipOps', function_name='update_supplier_category()')
            log.log(str(error), priority='highest')
            return exceptions.IncompleteRequestException('Failed to update supplier category, please try again')
        except Exception as e:
            log = Logger(module_name='SupplierRelationshipOps', function_name='update_supplier_category()')
            log.log(traceback.format_exc(), priority='highest')
            return exceptions.IncompleteRequestException('Failed to update supplier category, please try again')

    def get_supplier_categories(self):
        try:
            self.__cursor.execute("""select distinct(supplier_category) from supplier_relationships where buyer_id = %s""",
                                  (self.__id, ))
            res = self.__cursor.fetchall()
            if res is None:
                result = []
            result = [x['supplier_category'] for x in res if x['supplier_category'].lower() != "uncategorized"]
            return result

        except mysql.connector.Error as error:
            log = Logger(module_name='SupplierRelationshipOps', function_name='get_supplier_categories()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='SupplierRelationshipOps', function_name='get_supplier_categories()')
            log.log(traceback.format_exc(), priority='highest')
            return []

# pprint(SupplierRelationship(1000).get_supplier_categories())
# pprint(SupplierRelationship(1000).get_buyer_suppliers())
# pprint(SupplierRelationship("").add_supplier_relationship(1000, 1001))