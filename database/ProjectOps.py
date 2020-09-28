import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class Project:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__project = {}
        if self.__id != "":
            self.__cursor.execute("""select * from projects where project_id = %s""", (self.__id, ))
            self.__project = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_project(self, project_name, project_deadline, project_utc_deadline, project_budget, project_description="", ref_id=""):
        self.__project['project_name'], self.__project['project_description'] = project_name, project_description
        self.__project['project_budget'], self.__project['ref_id'] = project_budget, ref_id
        self.__project['project_deadline'], self.__project['project_utc_deadline'] = project_deadline, project_utc_deadline
        self.__project['project_id'] = self.insert(self.__project)
        return self.__project['project_id']

