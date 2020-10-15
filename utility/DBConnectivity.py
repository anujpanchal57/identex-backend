from pprint import pprint
import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient
from utility import conf
from redis import StrictRedis

def create_sql_connection():
    connection = mysql.connector.connect(host=conf.SQL_CONNECTION_URL,
                                         database=conf.sqlconfig.get('database_name'),
                                         user=conf.SQL_CONNECTION_USER,
                                         password=conf.SQL_CONNECTION_PASSWORD,
                                         autocommit=True)
    if connection.is_connected():
        return connection

def create_redis_connection():
    return StrictRedis(host=conf.redisconfig.get('host'), port=conf.redisconfig.get('port'))

def get_redis_key(key):
    redis = create_redis_connection()
    return redis.get(key)

# ,timeout=conf.OTPtimeout
def set_redis_key(key,value, timeout):
    redis = create_redis_connection()
    redis.set(key, value)
    redis.expire(key, timeout)
    return True

def delete_redis_key(key):
    redis = create_redis_connection()
    return redis.delete(key)

# pprint(create_sql_connection())
# pprint(delete_redis_key("sample"))
# pprint(set_redis_key("as", "we", 10))
# pprint(get_redis_key("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1OTYyMTUxODIsInVzZXIiOiJhbnVqcGFuY2hhbDU3QGdtYWlsLmNvbSJ9.gelgJLuNswaUonEuCITuvsdhDcqLclkEbGlljqD_WHc:8cb8b19057a2401ab300108c41d03aef"))
