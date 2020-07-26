from functionality import GenericOps
from utility import DBConnectivity, conf

class Authorization:
    def __init__(self, _id=""):
        self.__id = _id
        self.__mongo = DBConnectivity.create_mongo_connection()
        self.__auth = {}
        if self.__id != "":
            self.__auth = self.__mongo[conf.mongoconfig.get('tables').get("authorization_table")].find_one({"_id": self.__id})

    def login_user(self, auth_id, logged_in, buyer_id, email, device_name):
        self.__auth['_id'] = auth_id
        self.__auth['logged_in'] = logged_in
        self.__auth['buyer_id'] = buyer_id
        self.__auth['email'] = email
        self.__auth['device_name'] = device_name
        return self.save()

    def logout_user(self, logged_out, action_type):
        self.__auth['logged_out'] = logged_out
        self.__auth['action_type'] = action_type
        return self.save()

    def save(self, obj='', table='authorization_table'):
        if obj == '':
            return self.__mongo[conf.mongoconfig.get('tables').get(table)].update({'_id': self.__auth['_id']},
                                                                                  {"$set": self.__auth},
                                                                                  upsert=True)
        return self.__mongo[conf.mongoconfig.get('tables').get(table)].update({'_id': obj['_id']}, {"$set": obj},
                                                                              upsert=True)