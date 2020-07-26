from functionality import GenericOps
from utility import DBConnectivity, conf

class BuyerTeam:
    def __init__(self, _id=""):
        self.__id = _id
        self.__mongo = DBConnectivity.create_mongo_connection()
        self.__bteam = {}
        if self.__id != "":
            self.__bteam = self.__mongo[conf.mongoconfig.get("buyer_teams_table")].find_one({"_id": self.__id})

    @staticmethod
    def generate_team_id(buyer_id, team_name):
        return buyer_id + ":" + '_'.join(team_name.split(' '))

    @staticmethod
    def validate_team_name(buyer_id, team_name):
        return True if DBConnectivity.create_mongo_connection()[
            conf.mongoconfig.get('tables').get('buyer_teams_table')].find_one(
            {'buyer_id': buyer_id, "team_name": team_name}) is not None else False

    def create_team(self, team_name, buyer_id, members=[]):
        self.__bteam['_id'] = self.generate_team_id(buyer_id, team_name)
        self.__bteam['buyer_id'] = buyer_id
        self.__bteam['team_name'] = team_name
        self.__bteam['members'] = members
        timestamp = GenericOps.get_current_timestamp()
        self.__bteam['created_at'] = timestamp
        self.__bteam['updated_at'] = timestamp
        return self.save()

    def save(self, obj='', table='buyer_teams_table'):
        if obj == '':
            return self.__mongo[conf.mongoconfig.get('tables').get(table)].update({'_id': self.__bteam['_id']},
                                                                                  {"$set": self.__bteam},
                                                                                  upsert=True)
        return self.__mongo[conf.mongoconfig.get('tables').get(table)].update({'_id': obj['_id']}, {"$set": obj},
                                                                              upsert=True)

    def add_member(self, email):
        if 'members' not in self.__bteam:
            self.__bteam['members'] = []
        if email not in self.__bteam['members']:
            self.__bteam['members'].append(email)
        return self.save()