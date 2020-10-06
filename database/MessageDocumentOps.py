import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class MessageDocument:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__msg_doc = {}
        if self.__id != "":
            self.__cursor.execute("""select * from message_documents where document_id = %s""", (self.__id, ))
            self.__msg_doc = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_document(self, operation_id, operation_type, entity_id, document_url, document_type, document_name, uploaded_on, uploaded_by, uploader):
        self.__msg_doc['operation_id'] = operation_id
        self.__msg_doc['operation_type'] = operation_type
        self.__msg_doc['entity_id'] = entity_id
        self.__msg_doc['document_url'] = document_url
        self.__msg_doc['document_name'] = document_name
        self.__msg_doc['document_type'] = document_type
        self.__msg_doc['uploaded_on'] = uploaded_on
        self.__msg_doc['uploaded_by'] = uploaded_by
        self.__msg_doc['uploader'] = uploader
        return self.insert(self.__msg_doc)

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.message_documents_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO message_documents (operation_id, operation_type, entity_id, document_url, document_type, document_name, 
            uploaded_on, uploaded_by, uploader) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['operation_id'], values['operation_type'], values['entity_id'], values['document_url'],
                                   values['document_type'], values['document_name'], values['uploaded_on'],
                                   values['uploaded_by'], values['uploader']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='MessageDocumentOps', function_name='insert()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add document, please try again')
        except Exception as e:
            log = Logger(module_name='MessageDocumentOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add document, please try again')

    def insert_many(self, values):
        try:
            self.__cursor.execute(Implementations.message_documents_create_table)
            # Inserting the record in the table
            self.__cursor.executemany("""INSERT INTO message_documents (operation_id, operation_type, entity_id, document_url, document_type, document_name, 
            uploaded_on, uploaded_by, uploader) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", values)
            self.__sql.commit()
            last_row_id = self.__cursor.lastrowid
            result_ids = [last_row_id]
            for x in range(1, len(values)):
                result_ids.append(last_row_id + x)
            return result_ids

        except mysql.connector.Error as error:
            log = Logger(module_name='MessageDocumentOps', function_name='insert_many()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add document(s), please try again')
        except Exception as e:
            log = Logger(module_name='MessageDocumentOps', function_name='insert_many()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add document(s), please try again')

    def get_docs(self, entity_id, operation_type):
        self.__cursor.execute("""select document_name, document_type, document_url, uploaded_on, uploaded_by from message_documents 
        where entity_id = %s and operation_type = %s order by uploaded_on desc""", (entity_id, operation_type, ))
        res = self.__cursor.fetchall()
        self.__sql.commit()
        return res

    def get_message_docs(self, operation_id, operation_type):
        self.__cursor.execute("""select document_name, document_type, document_url, uploaded_on, uploaded_by from message_documents 
                where operation_id = %s and operation_type = %s""", (operation_id, operation_type,))
        res = self.__cursor.fetchall()
        self.__sql.commit()
        return res
# pprint(Document().insert_many([(1000, "rfq", "adsfdsafdsaf", "product", "product", 351321651, 1000, "buyer"),
#                                (1000, "rfq", "adsfdsafdsaf", "product", "product", 351321651, 1000, "buyer")]))

# pprint(Document().get_docs(1001, "product"))