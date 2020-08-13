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

SQL_CONNECTION_URL = conf_settings.get('sql').get('connection_url')

SQL_CONNECTION_USER = conf_settings.get('sql').get('user')

SQL_CONNECTION_PASSWORD = conf_settings.get('sql').get('password')

JWT_SECRET_KEY = conf_settings.get('secret').get('jwt')

PEPIPOST_API_KEY = conf_settings.get('api_keys').get('pepipost')

MAILGUN_API_KEY = conf_settings.get('api_keys').get('mailgun')

ENV_ENDPOINT = conf_settings.get('endpoint')

SUPPLIERS_ENDPOINT = conf_settings.get('suppliers_endpoint')

BUYER_ACTIVATION_SECRET_KEY = conf_settings.get('secret').get('buyer_activation')

aws = {
    'access_key': conf_settings['aws']['access_key_id'],
    'secret_key': conf_settings['aws']['secret_key'],
    'bucket_name': {
        'uploads': 'uploads-idntx'
    }
}

email_endpoints = {
    "buyer": {
        "email_verification": {
            "page_url": "/verify-email",
            "subject": "Verify your email",
            "template_id": "email_verification"
        },
        "welcome_mail": {
            "page_url": "",
            "subject": "Identex account activated",
            "template_id": "welcome_mail"
        },
        "forgot_password": {
            "page_url": "/reset-password",
            "subject": "Reset your password",
            "template_id": "forgot_password"
        },
        "supplier_onboarding": {
            "page_url": "",
            "subject": "You have been invited you to join Identex",
            "template_id": "supplier_onboarding"
        },
        "rfq_created": {
            "page_url": "",
            "subject": "You have received a RFQ from {{buyer_company}} for {{lot_name}}",
            "template_id": "rfq_created"
        }
    },
    "supplier": {
        "email_verification": {
            "page_url": "/verify-email",
            "subject": "Verify your email",
            "template_id": "email_verification"
        },
        "forgot_password": {
            "page_url": "/reset-password",
            "subject": "Reset your password",
            "template_id": "forgot_password"
        },
        "quotation_submitted": {
            "page_url": "",
            "subject": "{{supplier_company_name}} has submitted a quotation against RFQ: #{{requisition_id}}",
            "template_id": "quotation_submitted"
        }
    }
}

default_recipient = "archives.identex@gmail.com"