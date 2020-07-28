import requests
import json
from pprint import pprint
from utility import conf

# SENDING TEMPLATE EMAIL
def send_template_mail(subject, template, recipients=[], sender='', **kwargs):

    request_url = "https://api.mailgun.net/v3/delivery.identex.io/messages"
    # recipients.append(conf.default_recipient)
    auth = ("api", conf.MAILGUN_API_KEY)
    data = {
        "from": sender,
        "to": recipients,
        "subject": subject,
        "template": template
    }
    for name, value in kwargs.items():
        data['v:'+name.upper()] = str(value)
    return True if requests.post(request_url, auth=auth, data=data).status_code == 200 else False

# pprint(send_template_email(template_id=23076, subject="Welcome to Identex!", recipient=["anujpanchal57@gmail.com"]))
