import traceback
import urllib
import urllib.request
import urllib.parse
import requests
import json
from pprint import pprint
from utility import conf
from functionality import GenericOps

# SENDING TEMPLATE EMAIL
def send_template_mail(subject, template, recipients=[], sender='Identex <business@identex.io>', cc=[], bcc=[], **kwargs):

    request_url = "https://api.mailgun.net/v3/delivery.identex.io/messages"
    cc.append(conf.default_recipient)
    auth = ("api", conf.MAILGUN_API_KEY)
    data = {
        "from": sender,
        "to": recipients,
        "cc": cc,
        "subject": subject,
        "template": template
    }
    for name, value in kwargs.items():
        data['v:'+name.upper()] = str(value)

    return True if requests.post(request_url, auth=auth, data=data).status_code == 200 else False

def send_mail(subject, message, recipients=[], sender="Identex <business@identex.io>", cc=[], bcc=[]):
    request_url = "https://api.mailgun.net/v3/delivery.identex.io/messages"
    cc.append(conf.default_recipient)
    auth = ("api", conf.MAILGUN_API_KEY)
    data = {
        "from": sender,
        "to": recipients,
        "cc": cc,
        "subject": subject,
        "html": message
    }
    return True if requests.post(request_url, auth=auth, data=data).status_code == 200 else False

# Separate method for handling message based email alerts
def send_message_email(subject, template, recipients=['anuj.panchal@identex.io'],cc=[],bcc=[], sender='Identex <business@identex.io>', **kwargs):
    request_url = "https://api.mailgun.net/v3/delivery.identex.io/messages"
    files = []
    cc = []
    cc.append(conf.default_recipient)

    # For attaching documents in the mail
    if len(kwargs['documents']) > 0:
        for doc in kwargs['documents']:
            files.append(("attachment", (doc['document_name'], urllib.request.urlopen(doc['document_url']).read())))

    # if template in conf.message_templates:
    file_path = conf.message_files[template]
    html_to_parse = GenericOps.populate_email_template_for_messages(file_path, kwargs)
    auth = ("api", conf.MAILGUN_API_KEY)
    data = {
        "from": sender,
        "to": recipients,
        "subject": subject,
        "cc": cc,
        "bcc": bcc,
        "html": str(html_to_parse)
    }
    return True if requests.post(request_url, auth=auth, files=files, data=data).status_code == 200 else False

# SENDING TEMPLATE EMAIL
def send_handlebars_email(subject, template, recipients=[], sender='Identex <business@identex.io>', cc=[], bcc=[], **kwargs):

    request_url = "https://api.mailgun.net/v3/delivery.identex.io/messages"
    cc.append(conf.default_recipient)
    auth = ("api", conf.MAILGUN_API_KEY)
    data = {
        "from": sender,
        "to": recipients,
        "cc": cc,
        "subject": subject,
        "template": template
    }
    sample = {}
    for name, value in kwargs.items():
        if isinstance(value, list):
            sample[name.upper()] = value
        else:
            sample[name.upper()] = str(value)
    data['h:X-Mailgun-Variables'] = json.dumps(sample)
    return True if requests.post(request_url, auth=auth, data=data).status_code == 200 else False

# pprint(send_template_mail(template="email_verification", subject="Verify your email", recipients=['anuj.panchal@identex.io']))
# pprint(send_mail("Alert", "<h1>Error in logger: </h1><br><p>Error: 1062 (23000): Duplicate entry '1000-1001' for key 'PRIMARY'</p>", ["anuj.panchal@identex.io"]))