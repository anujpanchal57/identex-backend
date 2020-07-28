from functionality import GenericOps
from utility import DBConnectivity, conf

class Supplier:
    def __init__(self, _id=""):
        self.__id = _id
        self.__mongo = DBConnectivity.create_mongo_connection()
        self.__supplier = {}
        if self.__id != "":
            self.__supplier = self.__mongo[conf.mongoconfig.get('tables').get("supplier_table")].find_one({"_id": self.__id})

    # For autoincrementing and generating the buyer id
    def __generate_supplier_id(self):
        obj = self.__mongo[conf.mongoconfig.get('tables').get('constants_table')].find_one()
        supplier_id = "IDNTXS" + str(obj['supplier_id_counter'])
        obj['supplier_id_counter'] += 1
        self.save(obj, table="constants_table")
        return supplier_id

    # Adding a new supplier
    def add_supplier(self, company_name, activation_status=True, company_logo=""):
        self.__supplier['_id'] = self.__generate_supplier_id()
        self.__supplier['company_name'] = company_name
        self.__supplier['activation_status'] = activation_status
        self.__supplier['company_logo'] = company_logo
        timestamp = GenericOps.get_current_timestamp()
        self.__supplier['created_at'] = timestamp
        self.__supplier['updated_at'] = timestamp
        self.save()
        return self.__supplier['_id']

    def get_company_logo(self):
        return self.__supplier['company_logo']

    def get_company_name(self):
        return self.__supplier['company_name']

    def get_activation_status(self):
        return self.__supplier['activation_status']

    def save(self, obj='', table='supplier_table'):
        if obj == '':
            return self.__mongo[conf.mongoconfig.get('tables').get(table)].update({'_id': self.__supplier['_id']},
                                                                                  {"$set": self.__supplier},
                                                                                  upsert=True)
        return self.__mongo[conf.mongoconfig.get('tables').get(table)].update({'_id': obj['_id']}, {"$set": obj},
                                                                              upsert=True)

    def add_buyer(self, buyer_id):
        if 'buyer_id' not in self.__supplier:
            self.__supplier['buyer_id'] = []
            self.__supplier['buyer_id'].append(buyer_id)
            return self.save()
        if buyer_id not in self.__supplier['buyer_id']:
            self.__supplier['buyer_id'].append(buyer_id)
            return self.save()
        return True
