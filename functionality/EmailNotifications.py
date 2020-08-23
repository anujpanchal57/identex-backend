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
    # cc.append(conf.default_recipient)
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
    # cc.append(conf.default_recipient)
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
    # cc.append(conf.default_recipient)

    # For attaching documents in the mail
    if 'documents' not in kwargs:
        count = len([x for x in kwargs if 'document_name' in x])

        for x in range(0, count):
            files.append(("attachment", (kwargs['document_name_' + str(x+1)] + '.' + kwargs['document_content_' + str(x+1)].split('.')[-1],
                                         urllib.request.urlopen(kwargs['document_content_' + str(x+1)]).read()
                                         if GenericOps.is_url(kwargs['document_content_' + str(x+1)]) else open(
                                             kwargs['document_content_' + str(x+1)], 'rb').read())))
    elif template in ["cha_message_customer_agent", "chat_agent", "cha_message"]:
        if 'documents' in kwargs:
            if len(kwargs['documents']) > 0:
                for i in range(0, len(kwargs['documents'])):
                    files.append(('attachment', ( kwargs['documents'][i]['document_name'], urllib.request.urlopen(kwargs['documents'][i]['url']).read())))
    else:
        if len(kwargs['documents']) > 1:
            for i in range(0, len(kwargs['documents'])):
                files.append(('attachment', ('Booking Confirmation ' + str(i+1) + '.' + str(kwargs['documents'][i].split('.')[-1]),
                                             urllib.request.urlopen(kwargs['documents'][i]).read())))
        else:
            files.append(('attachment', ('Booking Confirmation' + '.' + str(kwargs['documents'][0].split('.')[-1]),
                                         urllib.request.urlopen(kwargs['documents'][0]).read())))

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


# pprint(send_template_mail(template="email_verification", subject="Verify your email", recipients=['anuj.panchal@identex.io']))
# pprint(send_mail("Alert", "<h1>Error in logger: </h1><br><p>Error: 1062 (23000): Duplicate entry '1000-1001' for key 'PRIMARY'</p>", ["anuj.panchal@identex.io"]))