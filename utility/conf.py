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

redisconfig = conf.get("redis")

user_log = conf.get("user_log")

sqlconfig = conf.get("sqlconfig")

jwt_expiration = conf.get("jwt").get('expire_after')

JWT_SECRET_KEY = conf_settings.get('secret').get('jwt')

PEPIPOST_API_KEY = conf_settings.get('api_keys').get('pepipost')

MAILGUN_API_KEY = conf_settings.get('api_keys').get('mailgun')

email_endpoints = {
    "development": {
        "verify_email": "http://localhost/verify/email",
        "buyer_forgot_password": "http://locahost/buyer/forgot/password",
        "supplier_forgot_password": "http://localhost/supplier/forgot/password"
    },
    "testing": {
        "verify_email": "http://testing.identex.io/verify/email",
        "buyer_forgot_password": "http://testing.identex.io/buyer/forgot/password",
        "supplier_forgot_password": "http://testing.identex.io/supplier/forgot/password"
    },
    "production": {
        "verify_email": "http://identex.io/verify/email",
        "buyer_forgot_password": "http://identex.io/buyer/forgot/password",
        "supplier_forgot_password": "http://identex.io/supplier/forgot/password"
    }
}

default_recipient = "accounts@identex.io"