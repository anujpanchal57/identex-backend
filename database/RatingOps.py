import traceback

from functionality import GenericOps
from utility import DBConnectivity, conf, Implementations
from functionality.Logger import Logger
from pprint import pprint
import mysql.connector
from exceptions import exceptions

class Rating:
    def __init__(self, _id=""):
        self.__id = _id
        self.__sql = DBConnectivity.create_sql_connection()
        self.__cursor = self.__sql.cursor(dictionary=True)
        self.__rating = {}
        if self.__id != "":
            self.__cursor.execute("""select * from ratings where rating_id = %s""", (self.__id, ))
            self.__rating = self.__cursor.fetchone()

    # For closing the connection
    def __del__(self):
        if self.__sql.is_connected():
            self.__cursor.close()
            self.__sql.close()

    def add_rating(self, client_id, client_type, receiver_id, receiver_type, acquisition_id, acquisition_type, rating, review=""):
        self.__rating['client_id'], self.__rating['client_type'] = client_id, client_type
        self.__rating['receiver_id'], self.__rating['receiver_type'] = receiver_id, receiver_type
        self.__rating['acquisition_id'], self.__rating['acquisition_type'] = acquisition_id, acquisition_type
        self.__rating['rating'] = rating
        self.__rating['review'] = review
        self.__rating['updated_at'] = GenericOps.get_current_timestamp()
        self.__rating['rating_id'] = self.insert(self.__rating)
        return self.__rating['rating_id']

    def insert(self, values):
        try:
            self.__cursor.execute(Implementations.ratings_create_table)
            # Inserting the record in the table
            self.__cursor.execute("""INSERT INTO ratings (client_id, client_type, receiver_id, receiver_type, acquisition_id, 
                                    acquisition_type, rating, updated_at, review) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                  (values['client_id'], values['client_type'], values['receiver_id'],
                                   values['receiver_type'], values['acquisition_id'], values['acquisition_type'],
                                   values['rating'], values['updated_at'], values['review']))
            self.__sql.commit()
            return self.__cursor.lastrowid

        except mysql.connector.Error as error:
            log = Logger(module_name='RatingOps', function_name='insert()')
            log.log(str(error), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add rating, please try again')
        except Exception as e:
            log = Logger(module_name='RatingOps', function_name='insert()')
            log.log(traceback.format_exc(), priority='highest')
            raise exceptions.IncompleteRequestException('Failed to add rating, please try again')

    def get_avg_rating(self, receiver_id, receiver_type):
        try:
            self.__cursor.execute("""select avg(rating) as avg_rating from ratings
                                    where receiver_id = %s and receiver_type = %s""",
                                  (receiver_id, receiver_type))
            res = self.__cursor.fetchone()['avg_rating']
            if res is None:
                res = 0
            return res

        except mysql.connector.Error as error:
            log = Logger(module_name='RatingOps', function_name='get_avg_rating()')
            log.log(str(error), priority='highest')
            return 0
        except Exception as e:
            log = Logger(module_name='RatingOps', function_name='get_avg_rating()')
            log.log(traceback.format_exc(), priority='highest')
            return 0

# pprint(Rating().add_rating(1000, "buyer", 1000, "supplier", 1000, "order", 3))
# pprint(Rating().get_avg_rating(1000, "supplier"))
