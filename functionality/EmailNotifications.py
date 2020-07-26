import requests
import json
from pprint import pprint
from utility import conf

def send_template_email(template_id, subject, recipient=[], sender="no-reply@identex.io", sender_name="Identex", **kwargs):
    url = "https://api.pepipost.com/v5/mail/send"
    payload_recipient = [{"email": x, "name": ""} for x in recipient]
    headers = {
        'api_key': conf.PEPIPOST_API_KEY,
        'content-type': "application/json"
    }
    payload = {
        "from": {
            "email": sender,
            "name": sender_name
        },
        "content": [{
            "type": "html",
            "value": " "
        }],
        "personalizations": [{
            "to": payload_recipient
        }],
        "subject": subject,
        "templateId": str(template_id)
    }
    response = requests.request("POST", url, data=json.dumps(payload, separators=(',', ':')), headers=headers)
    print(response.text)
    return True

# pprint(send_template_email(template_id=23076, subject="Welcome to Identex!", recipient=["anujpanchal57@gmail.com"]))
