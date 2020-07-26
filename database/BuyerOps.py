from functionality import GenericOps
from utility import DBConnectivity, conf

class Buyer:
    def __init__(self, _id=""):
        self.__id = _id
        self.__mongo = DBConnectivity.create_mongo_connection()
        self.__buyer = {}
        if self.__id != "":
            self.__buyer = self.__mongo[conf.mongoconfig.get('tables').get("buyer_table")].find_one({"_id": self.__id})

    # For autoincrementing and generating the buyer id
    def __generate_buyer_id(self):
        obj = self.__mongo[conf.mongoconfig.get('tables').get('constants_table')].find_one()
        buyer_id = "IDNTXB" + str(obj['buyer_id_counter'])
        obj['buyer_id_counter'] += 1
        self.save(obj, table="constants_table")
        return buyer_id

    # Adding a new buyer
    def add_buyer(self, company_name, domain_name, auto_join=True, default_currency="inr", subscription_plan="start", activation_status=False, company_logo="",
                  product_history=[]):
        self.__buyer['_id'] = self.__generate_buyer_id()
        self.__buyer['company_name'] = company_name
        self.__buyer['domain_name'] = domain_name
        self.__buyer['activation_status'] = activation_status
        self.__buyer['subscription_plan'] = subscription_plan
        self.__buyer['product_history'] = product_history
        self.__buyer['company_logo'] = company_logo
        self.__buyer['default_currency'] = default_currency
        self.__buyer['auto_join'] = auto_join
        self.__buyer['kyc_details'] = {}
        self.__buyer['teams'] = []
        timestamp = GenericOps.get_current_timestamp()
        self.__buyer['created_at'] = timestamp
        self.__buyer['updated_at'] = timestamp
        self.save()
        return self.__buyer['_id']

    def save(self, obj='', table='buyer_table'):
        if obj == '':
            return self.__mongo[conf.mongoconfig.get('tables').get(table)].update({'_id': self.__buyer['_id']},
                                                                                  {"$set": self.__buyer},
                                                                                  upsert=True)
        return self.__mongo[conf.mongoconfig.get('tables').get(table)].update({'_id': obj['_id']}, {"$set": obj},
                                                                              upsert=True)

    def get_activation_status(self):
        return self.__buyer['activation_status']

    def get_subscription_plan(self):
        return self.__buyer['subscription_plan']

    def get_auto_join(self):
        return self.__buyer['auto_join']

    def get_default_currency(self):
        return self.__buyer['default_currency']

    def get_company_logo(self):
        return self.__buyer['company_logo']