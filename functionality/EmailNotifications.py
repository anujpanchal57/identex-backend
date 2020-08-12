import requests
import json
from pprint import pprint
from utility import conf

# SENDING TEMPLATE EMAIL
def send_template_mail(subject, template, recipients=[], sender='Identex <business@identex.io>', **kwargs):

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

def send_mail(subject, message, recipients=[], sender="Identex <business@identex.io>"):
    request_url = "https://api.mailgun.net/v3/delivery.identex.io/messages"
    # recipients.append(conf.default_recipient)
    auth = ("api", conf.MAILGUN_API_KEY)
    data = {
        "from": sender,
        "to": recipients,
        "subject": subject,
        "html": message
    }
    return True if requests.post(request_url, auth=auth, data=data).status_code == 200 else False

# pprint(send_template_mail(template="email_verification", subject="Verify your email", recipients=["anujpanchal57@gmail.com"]))
# pprint(send_mail("Alert", "<h1>Error in logger: </h1><br><p>Error: 1062 (23000): Duplicate entry '1000-1001' for key 'PRIMARY'</p>", ["anuj.panchal@identex.io"]))