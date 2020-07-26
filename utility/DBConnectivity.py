from pprint import pprint

from pymongo import MongoClient
from utility import conf
from redis import StrictRedis

def create_mongo_connection():
    mongo = MongoClient(conf.mongoconfig.get('connection_url'))
    return mongo[conf.mongoconfig.get('database_name')]

def create_redis_connection():
    # return StrictRedis.from_url('redis://'+str(conf.redisconfig.get('host'))+':'+str(conf.redisconfig.get('port')))
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

# mongo = create_mongo_connection()
# pprint(mongo['user'].find_one({"_id": {'$regex': "gmail.com"}}))
