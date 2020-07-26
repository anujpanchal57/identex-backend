import json
import os
from pprint import pprint
import platform


app_name = '/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1])

# Reading data from settings.json
with open(app_name + '/settings.json') as f:
    conf_settings = json.load(f)

with open(app_name + '/conf.json') as f:
    conf = json.loads(f.read())

const = conf.get('const')

environ_name = "" if "environment_name" not in conf_settings else conf_settings['environment_name']

webconfig = conf.get("webconfig")

user_log = conf.get("user_log")

mongoconfig = conf.get("mongoconfig")

mongoconfig['connection_url'] = conf_settings.get('mongo').get('connection_url')

jwt_expiration = conf.get("jwt").get('expire_after')

JWT_SECRET_KEY = conf_settings.get('secret').get('jwt')

PEPIPOST_API_KEY = conf_settings.get('api_keys').get('pepipost')