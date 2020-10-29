import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class POAdditionalNotes:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__po_addl_note = {}
        if self.__id != "":
            self.__cursor.execute("""select * from po_additional_notes where note_id = %s""", (self.__id, ))
            self.__po_addl_note = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def get_template_name(self):
        return self.__po_addl_note['template_name']

    def get_template_config(self):
        return self.__po_addl_note['template_config']

    def get_note_id(self):
        return self.__po_addl_note['note_id']

    def add_po_additional_note(self, buyer_id, template_name, template_config):
        self.__po_addl_note['buyer_id'] = buyer_id
        self.__po_addl_note['template_name'] = template_name
        self.__po_addl_note['template_config'] = template_config
        self.__po_addl_note['note_id'] = self.insert(self.__po_addl_note)
        return self.__po_addl_note['note_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.po_additional_notes_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO po_additional_notes (buyer_id, template_name, template_config) 
                                    VALUES (%s, %s, %s)""",
                                  (values['buyer_id'], values['template_name'], values['template_config']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='POAdditionalNotesOps', function_name='insert()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add additional notes, please try again')
        except Exception as e:
            log = Logger(module_name='POAdditionalNotesOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add additional notes, please try again')

    def check_template_name(self, template_name, buyer_id):
        try:
            self.__cursor.execute("""select * from po_additional_notes where template_name = %s and buyer_id = %s""",
                                  (template_name, buyer_id))
            res = self.__cursor.fetchall()
            if res is None:
                return []
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='POAdditionalNotesOps', function_name='check_template_name()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='POAdditionalNotesOps', function_name='check_template_name()')
            log.log(traceback.format_exc(), priority='highest')
            return []

    def update_addl_note(self, template_details):
        try:
            self.__cursor.execute("""update po_additional_notes set template_name = %s, template_config = %s where note_id = %s""",
                                  (template_details['template_name'], template_details['template_config'], self.__id))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='POAdditionalNotesOps', function_name='update_addl_note()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to update additional note, please try again')
        except Exception as e:
            log = Logger(module_name='POAdditionalNotesOps', function_name='update_addl_note()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to update additional note, please try again')

    def get_addl_notes(self, buyer_id):
        try:
            self.__cursor.execute("""select template_name, note_id from po_additional_notes where buyer_id = %s""", (buyer_id, ))
            res = self.__cursor.fetchall()
            if res is None:
                return []
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='POAdditionalNotesOps', function_name='get_addl_notes()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='POAdditionalNotesOps', function_name='get_addl_notes()')
            log.log(traceback.format_exc(), priority='highest')
            return []

    def get_addl_note(self):
        try:
            self.__cursor.execute("""select * from po_additional_notes where note_id = %s""", (self.__id, ))
            res = self.__cursor.fetchone()
            if res is None:
                return []
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='POAdditionalNotesOps', function_name='get_addl_note()')
            log.log(str(error), priority='highest')
            return []
        except Exception as e:
            log = Logger(module_name='POAdditionalNotesOps', function_name='get_addl_note()')
            log.log(traceback.format_exc(), priority='highest')
            return []