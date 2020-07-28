from pprint import pprint

import jwt

from functionality import GenericOps
from utility import DBConnectivity, conf
from exceptions import exceptions
from database.AuthorizationOps import Authorization

class SUser:
    def __init__(self, _id=""):
        self.__id = _id
        self.__mongo = DBConnectivity.create_mongo_connection()
        self.__suser = {}
        if self.__id != "":
            self.__suser = self.__mongo[conf.mongoconfig.get('tables').get('suser_table')].find_one({"_id": self.__id})

    # Adding a new user for a buyer company
    def add_suser(self, email, name, supplier_id, password, mobile_no="", role="admin", status=True):
        self.__suser['_id'] = email
        self.__suser['name'] = name
        self.__suser['mobile_no'] = mobile_no
        self.__suser['supplier_id'] = supplier_id
        self.__suser['password'] = password
        self.__suser['role'] = role
        self.__suser['status'] = status
        self.__suser['tokens'] = []
        timestamp = GenericOps.get_current_timestamp()
        self.__suser['created_at'] = timestamp
        self.__suser['updated_at'] = timestamp
        return self.save()

    @staticmethod
    def is_suser(email):
        return DBConnectivity.create_mongo_connection()[conf.mongoconfig.get('tables').get('suser_table')].find_one(
            {"_id": email}) if DBConnectivity.create_mongo_connection()[conf.mongoconfig.get('tables').get('suser_table')].find_one({"_id": email}) is not None else False

    def verify_auth_token(self, token_name='', token_value =''):
        for index in range(0, len(self.__suser['tokens'])):
            if self.__suser['tokens'][index]['token_name'] == token_name and self.__suser['tokens'][index]['token_value'] == token_value:
                self.__suser['status'] = True
                del self.__suser['tokens'][index]
                return self.save()
        return False

    def add_auth_token(self, token_value='', token_name='forgot_password'):
        if len(self.__suser['tokens']) > 0:
            for index in range(0, len(self.__suser['tokens'])):
                if token_value == self.__suser['tokens'][index]['token_value']:
                    return True
            self.__suser['tokens'].append({"token_name": token_name, "token_value": token_value})
            return self.save()
        self.__suser['tokens'].append({"token_name": token_name, "token_value": token_value})
        return self.save()

    def delete_auth_token(self, token_name='', token_value=''):
        for index in range(0, len(self.__suser['tokens'])):
            if self.__suser['tokens'][index]['token_name'] == token_name and self.__suser['tokens'][index]['token_value'] == token_value:
                del self.__suser['tokens'][index]
                return self.save()
        return False

    def get_name(self):
        return self.__suser['name']

    def get_mobile_no(self):
        return self.__suser['mobile_no']

    def get_buyer_id(self):
        return self.__suser['buyer_id']

    def get_password(self):
        return self.__suser['password']

    def get_role(self):
        return self.__suser['role']

    def get_status(self):
        return self.__suser['status']

    def get_created_at(self):
        return self.__suser['created_at']

    def get_updated_at(self):
        return self.__suser['updated_at']

    def set_password(self, password):
        self.__suser['password'] = password
        return self.save()

    def get_supplier_id(self):
        return self.__suser['supplier_id']

    @staticmethod
    def is_suser(email):
        return DBConnectivity.create_mongo_connection()[conf.mongoconfig.get('tables').get('suser_table')].find_one(
            {"_id": email}) if DBConnectivity.create_mongo_connection()[conf.mongoconfig.get('tables').get('suser_table')].find_one({"_id": email}) is not None else False

    def get_email(self):
        return self.__suser['_id']

    # Encoding JWT token with an expiration time of 3 days
    def encode_auth_token(self):
        return (jwt.encode({"user": self.get_email(), "exp": GenericOps.get_current_timestamp() + conf.jwt_expiration}, conf.JWT_SECRET_KEY, algorithm="HS256")).decode('UTF-8')

    # Decoding a JWT token
    def decode_auth_toke(self, token):
        try:
            decode = jwt.decode(token, conf.JWT_SECRET_KEY, algorithms=['HS256'])
            return decode
        except jwt.ExpiredSignatureError as e:
            return str(e)

    def save(self, obj='', table='suser_table'):
        if obj == '':
            return self.__mongo[conf.mongoconfig.get('tables').get(table)].update({'_id': self.__suser['_id']},
                                                                                  {"$set": self.__suser},
                                                                                  upsert=True)
        return self.__mongo[conf.mongoconfig.get('tables').get(table)].update({'_id': obj['_id']}, {"$set": obj},
                                                                              upsert=True)



# suser = SUser("anujpanchal57@gmail.com")
# pprint(suser.encode_auth_token())
# pprint(suser.decode_auth_toke())