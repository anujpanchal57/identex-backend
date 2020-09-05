import base64
import calendar
import datetime
from datetime import timedelta, timezone
import random
import re
import string
import time
import math
import uuid
import random
import string
from pprint import pprint
import bs4
import pytz

from utility import DBConnectivity
from utility import conf


def get_current_timestamp(rounded=True):
    return math.ceil(time.time()) if rounded else time.time()

def convert_datestring_to_timestamp(date_str, format="%d-%m-%Y"):
    return int(datetime.datetime.strptime(date_str, format).timestamp())

def round_of(number, number_of_decimals=2):
    try:
        return round(number, number_of_decimals)
    except Exception as e:
        return number

def convert_datetime_to_utc_datetimestring(datetime_str, op_tz, in_format="%d-%m-%Y %H:%M", out_format="%Y-%m-%d %H:%M"):
    # dt = datetime.datetime.strptime(datetime_str, in_format)
    # ts = int(dt.replace(tzinfo=timezone.utc).timestamp())
    offset = datetime.datetime.now(pytz.timezone(op_tz)).strftime("%z")
    date_obj = datetime.datetime.strptime(datetime_str, in_format)
    ts = int(date_obj.replace(tzinfo=timezone.utc).timestamp())
    actual = convert_time_offset_to_timestamp(offset, ts)
    return datetime.datetime.fromtimestamp(actual).strftime(out_format)

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

def get_calculated_timestamp(date_time, op_tz):
    offset = datetime.datetime.now(pytz.timezone(op_tz)).strftime("%z")
    date_obj = datetime.datetime.strptime(date_time, "%d-%m-%Y %H:%M")
    ts = int(date_obj.replace(tzinfo=timezone.utc).timestamp())
    return convert_time_offset_to_timestamp(offset, ts)

def convert_time_offset_to_timestamp(offset, utc_timestamp):
    return int(utc_timestamp - ((int(offset[0:3]) * 60 * 60) + (int(offset[3:]) * 60)))

def calculate_operation_deadline(utc_deadline):
    utc_timestamp = int(datetime.datetime.utcnow().timestamp())
    deadline_ts = int(datetime.datetime.strptime(utc_deadline, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc).timestamp())
    time_remaining = deadline_ts - utc_timestamp
    return time_remaining

def get_current_timestamp_of_timezone(op_tz):
    tz = pytz.timezone(op_tz)
    offset = datetime.datetime.now(tz).strftime("%z")
    return convert_time_offset_to_timestamp(offset, int(datetime.datetime.utcnow().timestamp()))

def calculate_closing_time(utc_deadline, op_tz, in_format="%Y-%m-%d %H:%M", out_format="%d-%m-%Y %H:%M"):
    offset = datetime.datetime.now(pytz.timezone(op_tz)).strftime("%z")
    dt = datetime.datetime.strptime(utc_deadline, in_format)
    ts = int(dt.replace(tzinfo=timezone.utc).timestamp())
    result = datetime.datetime.fromtimestamp(add_offset_to_utc(offset, ts)).strftime(out_format)
    return result

def add_offset_to_utc(offset, utc_ts):
    return int(utc_ts + ((int(offset[0:3]) * 60 * 60) + (int(offset[3:]) * 60)))

def populate_email_template_for_messages(file_path, details):
    with open(file_path) as html:
        txt = html.read()
        soup = bs4.BeautifulSoup(txt, 'html.parser')
    params = {}
    params['USER'] = details['USER'] if 'USER' in details else ""
    message = details['MESSAGE'] if 'MESSAGE' in details else ""
    params['SENDER'] = details['SENDER'] if 'SENDER' in details else ""
    params['TYPE_OF_REQUEST'] = details['TYPE_OF_REQUEST'] if 'TYPE_OF_REQUEST' in details else ""
    params['REQUEST_ID'] = details['REQUEST_ID'] if 'REQUEST_ID' in details else ""
    params['LOT_NAME'] = details['LOT_NAME'] if 'LOT_NAME' in details else ""
    params['LINK_FOR_REPLY'] = details['LINK_FOR_REPLY'] if 'LINK_FOR_REPLY' in details else ""
    message_div = soup.find(id="message_div")
    message_div.append(bs4.BeautifulSoup(message, 'html.parser'))
    for key, val in params.items():
        soup = bs4.BeautifulSoup(str(soup).replace("{{" + str(key.upper()) + "}}", str(val)))
    return soup

# pprint(calculate_closing_time(1598376600, "asia/calcutta"))
# pprint(calculate_closing_time("2020-08-25 17:30", "asia/calcutta"))
# pprint(populate_email_template_for_messages(file_path=conf.message_files['message_received'], details={}))
# pprint(convert_datetime_to_utc_datetimestring("20-08-2020 02:00"))
# pprint(calculate_operation_deadline("asia/calcutta", 1597912200))
# pprint(datetime.datetime.utcnow().timestamp())
# pprint(convert_time_offset_to_timestamp("-0500", 1000000))
# pprint(generate_email_verification_token())
# pprint(get_current_timestamp_of_timezone('Asia/Aqtau'))