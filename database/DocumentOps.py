import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector

class Document:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__document = {}
        if self.__id != "":
            self.__cursor.execute("""select * from documents where document_id = %s""", (self.__id, ))
            self.__document = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_document(self, operation_id, operation_type, document_url, document_type, document_name, uploaded_on, uploaded_by, uploader):
        self.__document['operation_id'] = operation_id
        self.__document['operation_type'] = operation_type
        self.__document['document_url'] = document_url
        self.__document['document_name'] = document_name
        self.__document['document_type'] = document_type
        self.__document['uploaded_on'] = uploaded_on
        self.__document['uploaded_by'] = uploaded_by
        self.__document['uploader'] = uploader
        return self.insert(self.__document)

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.documents_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO documents (operation_id, operation_type, document_url, document_type, document_name, 
            uploaded_on, uploaded_by, uploader) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['operation_id'], values['operation_type'], values['document_url'],
                                   values['document_type'], values['document_name'], values['uploaded_on'],
                                   values['uploaded_by'], values['uploader']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='DocumentOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='DocumentOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def insert_many(self, values):
        try:
            self.__cursor.execute(Implementations.documents_create_table)
            # Inserting the record in the table
            self.__cursor.executemany("""INSERT INTO documents (operation_id, operation_type, document_url, document_type, document_name, 
            uploaded_on, uploaded_by, uploader) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", values)
            self.__sql.commit()
            last_row_id = self.__cursor.lastrowid
            result_ids = [last_row_id]
            for x in range(1, len(values)):
                result_ids.append(last_row_id + x)
            return result_ids

        except mysql.connector.Error as error:
            log = Logger(module_name='DocumentOps', function_name='insert_many()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='DocumentOps', function_name='insert_many()')
            log.log(traceback.format_exc(), priority='highest')
            return False

# pprint(Document().insert_many([(1000, "rfq", "adsfdsafdsaf", "product", "product", 351321651, 1000, "buyer"),
#                                (1000, "rfq", "adsfdsafdsaf", "product", "product", 351321651, 1000, "buyer")]))