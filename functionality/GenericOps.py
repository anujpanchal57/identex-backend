import base64
import calendar
import datetime
from datetime import timedelta
import random
import re
import string
import time

import math
import uuid
import random
import string
from pprint import pprint

import pytz

from utility import DBConnectivity
from utility import conf


def get_current_timestamp(rounded=True):
    return math.ceil(time.time()) if rounded else time.time()

def convert_datestring_to_timestamp(date_str, format="%d-%m-%Y"):
    return int(datetime.datetime.strptime(date_str, format).timestamp())

def generate_forgot_password_token():
    token = ''.join(str(uuid.uuid4()).split('-'))
    return token

def generate_email_verification_token():
    token = ''.join(str(uuid.uuid4()).split('-'))
    return token

def generate_token_for_login():
    link = ''.join(str(uuid.uuid4()).split('-'))
    return link

def generate_aws_file_path(client_type, client_id, document_type):
    if client_type.lower() == "buyer":
        return "B" + str(client_id) + "/" + ''.join(str(uuid.uuid4()).split('-')) + "." + document_type
    return "S" + str(client_id) + "/" + ''.join(str(uuid.uuid4()).split('-')) + "." + document_type

def is_url(url):
    return 'http://' in url or 'https://' in url

def generate_user_password(length=7):
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(length))

def get_calculated_timestamp(date_time):
    return datetime.datetime.strptime(date_time, "%d-%m-%Y %H:%M").timestamp()

# pprint(generate_email_verification_token())
# Time conversion template
# timezone = pytz.timezone("asia/calcutta")
# dt = datetime.datetime.now(timezone)
# pprint(dt)
# utc_dt = dt.astimezone(pytz.utc)
# pprint(dt.strftime("%z"))