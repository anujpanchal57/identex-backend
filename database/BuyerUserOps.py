from pprint import pprint

import jwt

from functionality import GenericOps
from utility import DBConnectivity, conf
from exceptions import exceptions
from database.AuthorizationOps import Authorization

class BUser:
    def __init__(self, _id=""):
        self.__id = _id
        self.__mongo = DBConnectivity.create_mongo_connection()
        self.__buser = {}
        if self.__id != "":
            self.__buser = self.__mongo[conf.mongoconfig.get('tables').get('buser_table')].find_one({"_id": self.__id})

    # Adding a new user for a buyer company
    def add_buser(self, email, name, buyer_id, mobile_no, password, role, status=False):
        self.__buser['_id'] = email
        self.__buser['name'] = name
        self.__buser['mobile_no'] = mobile_no
        self.__buser['buyer_id'] = buyer_id
        self.__buser['password'] = password
        self.__buser['role'] = role
        self.__buser['status'] = status
        timestamp = GenericOps.get_current_timestamp()
        self.__buser['created_at'] = timestamp
        self.__buser['updated_at'] = timestamp
        return self.save()

    def login(self, password, device_name):
        if self.__buser is not None:
            if self.__buser['password'] == password:
                if self.__buser['status']:
                    auth_id = self.encode_auth_token() + ":" + GenericOps.generate_token_for_login()
                    auth = Authorization().login_user(auth_id=auth_id, logged_in=GenericOps.get_current_timestamp(), buyer_id=self.get_buyer_id(),
                                                      email=self.__id, device_name=device_name)
                    return auth
                raise exceptions.InvalidLoginCredentials('Please verify your email and then try logging in')
            raise exceptions.InvalidLoginCredentials('You have entered incorrect password')
        raise exceptions.InvalidLoginCredentials('We cannot find an account with this email address')

    def logout(self, token):
        for i in range(len(self.__buser['authorization'])):
            if self.__buser['authorization'][i]['token'] == token:
                self.__buser['authorization'][i]['logged_in'] = False
                self.__buser['authorization'][i]['timestamp'] = GenericOps.get_current_timestamp()
                return self.save()
            return True

    @staticmethod
    def is_buser(email):
        return DBConnectivity.create_mongo_connection()[conf.mongoconfig.get('tables').get('buser_table')].find_one(
            {"_id": email}) if DBConnectivity.create_mongo_connection()[conf.mongoconfig.get('tables').get('buser_table')].find_one({"_id": email}) is not None else False

    @staticmethod
    def is_buser_domain_registered(email):
        company_domain = '@' + email.split('@')[1]
        return DBConnectivity.create_mongo_connection()[conf.mongoconfig.get('tables').get('buser_table')].find_one(
            {'_id': {'$regex': company_domain}}) if DBConnectivity.create_mongo_connection()[
                                                        conf.mongoconfig.get('tables').get('buser_table')].find_one(
            {'_id': {'$regex': company_domain}}) is not None else False

    def get_buyer_id(self):
        return self.__buser['buyer_id']

    def get_status(self):
        return self.__buser['status']

    def get_email(self):
        return self.__buser['_id']

    def get_name(self):
        return self.__buser['name']

    def get_mobile_no(self):
        return self.__buser['mobile_no']

    def get_status(self):
        return self.__buser['status']

    def get_password(self):
        return self.__buser['password']

    def get_created_at(self):
        return self.__buser['created_at']

    def get_updated_at(self):
        return self.__buser['updated_at']

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

    def save(self, obj='', table='buser_table'):
        if obj == '':
            return self.__mongo[conf.mongoconfig.get('tables').get(table)].update({'_id': self.__buser['_id']},
                                                                                  {"$set": self.__buser},
                                                                                  upsert=True)
        return self.__mongo[conf.mongoconfig.get('tables').get(table)].update({'_id': obj['_id']}, {"$set": obj},
                                                                              upsert=True)

    def is_admin(self):
        return True if self.__buser['role'].lower() == "admin" else False


# buser = BUser("anujpanchal57@gmail.com")
# pprint(buser.encode_auth_token())
# pprint(buser.decode_auth_toke())