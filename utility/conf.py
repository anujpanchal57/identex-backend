import json
import os
from pprint import pprint
import platform

app_name = '/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1])

##################################### For UBUNTU ###################################################
# Reading data from settings.json
with open(app_name + '/settings.json') as f:
    conf_settings = json.load(f)

with open(app_name + '/conf.json') as f:
    conf = json.loads(f.read())

##################################### For WINDOWS ###################################################
# Reading data from settings.json
# with open(app_name + 'settings.json') as f:
#     conf_settings = json.load(f)
#
# with open(app_name + 'conf.json') as f:
#     conf = json.loads(f.read())

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

SUPPLIERS_ENDPOINT = conf_settings.get('supplier_endpoint')

BUYER_ACTIVATION_SECRET_KEY = conf_settings.get('secret').get('buyer_activation')

APPY_FLOW_SECRET_KEY = conf_settings.get('api_keys').get('appyflow')

aws = {
    'access_key': conf_settings['aws']['access_key_id'],
    'secret_key': conf_settings['aws']['secret_key'],
    'bucket_name': {
        'uploads': conf_settings['aws']['bucket_name']
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
            "subject": "You have been invited to join Identex",
            "template_id": "supplier_onboarding"
        },
        "rfq_created": {
            "page_url": "/rfq?type=open",
            "subject": "You have received a RFQ from {{buyer_company}} for {{lot_name}}",
            "template_id": "rfq_created"
        },
        "cancel_rfq": {
            "page_url": "",
            "subject": "RFQ cancelled",
            "template_id": "cancel_rfq"
        },
        "change_in_deadline": {
            "page_url": "",
            "subject": "Deadline changed for RFQ: #{{requisition_id}}",
            "template_id": "change_in_deadline"
        },
        "unlock_supplier": {
            "page_url": "/rfq?type=open",
            "subject": "You have been unlocked by buyer to resubmit your quote for RFQ: #{{requisition_id}}",
            "template_id": "unlock_supplier"
        },
        "message_received": {
            "page_url": "/{{operation}}/live-{{operation}}?id={{operation_id}}&action={{action_type}}",
            "subject": "You have received a new message for {{operation_type}}: #{{requisition_id}}",
            "template_id": "message_received"
        },
        "cancel_order": {
            "page_url": "",
            "subject": "",
            "template_id": "cancel_order"
        },
        "order_created": {
            "page_url": "/orders?type=active",
            "subject": "",
            "template_id": "order_created"
        },
        "order_delivered": {
            "page_url": "/orders?type=delivered",
            "subject": "",
            "template_id": "order_delivered"
        },
        "invoice_paid": {
            "page_url": "/invoices?type=paid",
            "subject": "Invoice paid by {{buyer_company_name}}",
            "template_id": "invoice_paid"
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
            "page_url": "/rfq/live-rfq?id={{requisition_id}}&action=quotes",
            "subject": "{{supplier_company_name}} has submitted a quotation against RFQ: #{{requisition_id}}",
            "template_id": "quotation_submitted"
        },
        "rfq_created": {
            "page_url": "/rfq?type=open",
            "subject": "You have received a RFQ from {{buyer_company}} for {{lot_name}}",
            "template_id": "rfq_created"
        },
        "message_received": {
            "page_url": "/{{operation}}?type=open",
            "subject": "You have received a new message for {{operation_type}}: #{{requisition_id}}",
            "template_id": "message_received"
        },
        "invoice_raised": {
            "page_url": "/invoices?type=pending",
            "subject": "Invoice raised by {{supplier_name}}",
            "template_id": "invoice_raised"
        },
        "rank_changed": {
            "page_url": "/{{operation_type}}?type=open",
            "subject": "Your rank for the {{operation_type}} (#{{requisition_id}}) has changed",
            "template_id": "rank_changed"
        },
        "rfq_close_reminder": {
            "page_url": "/rfq?type=open",
            "subject": "Your RFQ[{}] from {} for {} is about to close!",
            "template_id": "rfq_closing_reminder_2hours"
        }
    }
}

message_files = {
    "message_received": app_name + "/templates/message_received.html"
}

default_recipient = "archives.identex@gmail.com"

default_founder_email = "utkarsh.dhawan@identex.io"

default_submission_limit = 3

all_quotations_excel_sample = app_name + "/templates/Supplier Quotations.xlsx"
invoice_excel_sample = app_name + "/templates/Invoice.xlsx"
quotations_summary_excel_sample = app_name + "/templates/Quotation Summary.xlsx"

