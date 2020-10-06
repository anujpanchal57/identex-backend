import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class ProjectMembers:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__proj_members = {}

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_project_member(self, project_id, member_email):
        self.__proj_members['project_id'], self.__proj_members['member_email'] = project_id, member_email
        return self.insert(self.__proj_members)

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.project_members_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO project_members (project_id, member_email) VALUES (%s, %s)""",
                                  (values['project_id'], values['member_email']))
            self.__sql.commit()
            return True

        except mysql.connector.Error as error:
            log = Logger(module_name='ProjectMemberOps', function_name='insert()')
            log.log(str(error), priority='highest')
            return False
        except Exception as e:
            log = Logger(module_name='ProjectMemberOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            return False

    def insert_many(self, values):
        try:
            self.__cursor.execute(Implementations.project_members_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO project_members (project_id, member_email) VALUES (%s, %s)""", values)
            self.__sql.commit()
            last_row_id = self.__cursor.lastrowid
            result_ids = [last_row_id]
            for x in range(1, len(values)):
                result_ids.append(last_row_id + x)
            return result_ids

        except mysql.connector.Error as error:
            log = Logger(module_name='ProjectMemberOps', function_name='insert_many()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add member(s), please try again')
        except Exception as e:
            log = Logger(module_name='ProjectMemberOps', function_name='insert_many()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add member(s), please try again')