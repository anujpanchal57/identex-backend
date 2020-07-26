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

from utility import DBConnectivity
from utility import conf


def get_current_timestamp(rounded=True):
    return math.ceil(time.time()) if rounded else time.time()

def generate_forgot_password_link():
    link = ''.join(str(uuid.uuid4()).split('-'))
    return link

def generate_token_for_login():
    link = ''.join(str(uuid.uuid4()).split('-'))
    return link

def is_url(url):
    return 'http://' in url or 'https://' in url

def generate_user_password(length=7):
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(length))

