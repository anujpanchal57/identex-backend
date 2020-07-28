from pprint import pprint

from pymongo import MongoClient
from utility import conf
from redis import StrictRedis

def create_mongo_connection():
    mongo = MongoClient(conf.mongoconfig.get('connection_url'))
    return mongo[conf.mongoconfig.get('database_name')]

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

# pprint(delete_redis_key("sample"))
# pprint(set_redis_key("as", "we", 10))
# pprint(get_redis_key("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1OTYyMTUxODIsInVzZXIiOiJhbnVqcGFuY2hhbDU3QGdtYWlsLmNvbSJ9.gelgJLuNswaUonEuCITuvsdhDcqLclkEbGlljqD_WHc:8cb8b19057a2401ab300108c41d03aef"))
# mongo = create_mongo_connection()
# pprint(mongo['user'].find_one({"_id": {'$regex': "gmail.com"}}))
