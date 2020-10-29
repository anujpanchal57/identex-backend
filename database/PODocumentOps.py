import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class PODocument:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__po_doc = {}
        if self.__id != "":
            self.__cursor.execute("""select * from po_documents where document_id = %s""", (self.__id, ))
            self.__po_doc = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_po_document(self, buyer_id, document_name, document_format, document_url, uploaded_on, uploaded_by, uploader="buyer"):
        self.__po_doc['buyer_id'] = buyer_id
        self.__po_doc['document_name'], self.__po_doc['document_format'] = document_name, document_format
        self.__po_doc['document_url'], self.__po_doc['uploaded_on'] = document_url, uploaded_on
        self.__po_doc['uploaded_by'], self.__po_doc['uploader'] = uploaded_by, uploader
        self.__po_doc['document_id'] = self.insert(self.__po_doc)
        return self.__po_doc['document_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.po_documents_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO po_documents (buyer_id, document_name, document_format, 
                                    document_url, uploaded_on, uploaded_by, uploader) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                  (values['buyer_id'], values['document_name'], values['document_format'],
                                   values['document_url'], values['uploaded_on'], values['uploaded_by'], values['uploader']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='PODocumentOps', function_name='insert()')
            log.log(str(error), priority='critical')
            raise exceptions.IncompleteRequestException('Failed to add document, please try again')
        except Exception as e:
            log = Logger(module_name='PODocumentOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='critical')
            raise exceptions.IncompleteRequestException('Failed to add document, please try again')

    def insert_many(self, values):
        try:
            self.__cursor.execute(Implementations.po_documents_create_table)
            # Inserting the record in the table
            self.__cursor.executemany("""INSERT INTO po_documents (buyer_id, document_name, document_format, 
                                        document_url, uploaded_on, uploaded_by, uploader) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)""", values)
            self.__sql.commit()
            last_row_id = self.__cursor.lastrowid
            result_ids = [last_row_id]
            for x in range(1, len(values)):
                result_ids.append(last_row_id + x)
            return result_ids

        except mysql.connector.Error as error:
            log = Logger(module_name='PODocumentOps', function_name='insert_many()')
            log.log(str(error), priority='critical')
            raise exceptions.IncompleteRequestException('Failed to insert PO documents, please try again')
        except Exception as e:
            log = Logger(module_name='PODocumentOps', function_name='insert_many()')
            log.log(traceback.format_exc(), priority='critical')
            raise exceptions.IncompleteRequestException('Failed to insert PO documents, please try again')

    def check_document_name(self, buyer_id, document_name):
        try:
            self.__cursor.execute("""select * from po_documents where document_name = %s and buyer_id = %s""",
                                      (document_name, buyer_id))
            res = self.__cursor.fetchall()
            if res is None:
                return []
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='PODocumentOps', function_name='check_document_name()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='PODocumentOps', function_name='check_document_name()')
            log.log(traceback.format_exc(), priority='highest')
            return []

    def delete_document(self):
        try:
            self.__cursor.execute("""delete from po_documents where document_id = %s""", (self.__id, ))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='PODocumentOps', function_name='delete_document()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to delete document, please try again')
        except Exception as e:
            log = Logger(module_name='PODocumentOps', function_name='delete_document()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to delete document, please try again')

    def get_frequent_uploaded_docs(self, buyer_id, limit=5):
        try:
            self.__cursor.execute("""select * from po_documents where buyer_id = %s order by frequency desc limit %s""",
                                      (buyer_id, limit))
            res = self.__cursor.fetchall()
            if res is None:
                return []
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='PODocumentOps', function_name='get_frequent_uploaded_docs()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='PODocumentOps', function_name='get_frequent_uploaded_docs()')
            log.log(traceback.format_exc(), priority='highest')
            return []

    def get_documents(self, buyer_id, limit=50):
        try:
            self.__cursor.execute("""select * from po_documents where buyer_id = %s order by frequency desc limit %s""",
                                  (buyer_id, limit))
            res = self.__cursor.fetchall()
            if res is None:
                return []
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='PODocumentOps', function_name='get_documents()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='PODocumentOps', function_name='get_documents()')
            log.log(traceback.format_exc(), priority='highest')
            return []

    def update_frequency(self, documents):
        try:
            if 0 < len(documents) <= 1:
                doc_ids = documents[0]['document_id']
                self.__cursor.execute("""update po_documents set frequency = frequency + 1 where document_id = %s""",
                                      (doc_ids, ))
                self.__sql.commit()
                return True
            else:
                doc_ids = []
                for doc in documents:
                    doc_ids.append(doc['document_id'])
                self.__cursor.execute("""update po_documents set frequency = frequency + 1 where document_id in %s""", (doc_ids, ))
                self.__sql.commit()
                return True

        except mysql.connector.Error as error:
            log = Logger(module_name='PODocumentOps', function_name='update_frequency()')
            log.log(str(error), priority='critical')
            raise exceptions.IncompleteRequestException('Failed to update document frequency, please try again')
        except Exception as e:
            log = Logger(module_name='PODocumentOps', function_name='update_frequency()')
            log.log(traceback.format_exc(), priority='critical')
            raise exceptions.IncompleteRequestException('Failed to update document frequency, please try again')