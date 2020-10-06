import json
import os
import re
import sys
from pprint import pprint
import traceback

import requests
from bs4 import BeautifulSoup
app_name = '/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1])

sys.path.append(app_name)

from utility import DBConnectivity

spot_url = "https://www.mcxindia.com/market-data/spot-market-price"


def get_spot_rates():
    counter = 0
    for script in BeautifulSoup(requests.get(spot_url).text).find_all("script"):
        if script.string is not None:
            if len(script.string.split("var vSMP="))>1:
                break
        counter += 1
    page_source = BeautifulSoup(requests.get(spot_url).text).find_all("script")[counter].string.replace("//<![CDATA[","").replace(";//]]>","").replace("var vSMP=","").strip()
    data = json.loads(page_source.split(';')[0])
    count = 0
    for spot_rate in data['Data']:
        spot_rate['Date'] = int(spot_rate['Date'].replace('/Date(','').replace(')/',''))
        data['Data'][count] = spot_rate
    data['Summary']['AsOn'] = int(data['Summary']['AsOn'].replace('/Date(','').replace(')/',''))
    sql = DBConnectivity.create_sql_connection()
    cursor = sql.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT * FROM `mcx_update_history` ORDER BY `as_on` DESC LIMIT 1""")
        update_history = cursor.fetchone()
        if update_history is not None and data['Summary']['AsOn'] > update_history['as_on']:
            cursor.execute("""UPDATE `mcx_spot_rate` SET `status`=0 WHERE 1""")
            for d in data['Data']:
                cursor.execute("""INSERT INTO `mcx_spot_rate` (`spot_id`, `spot_symbol`, `location`, `spot_price`, `unit`, `unit_currency`, `updated_on`, `change_amount`)
                VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)""", (d['Symbol'], d['Location'], d['TodaysSpotPrice'], d['Unit'], 'inr', d['Date'], d['Change']))
            cursor.execute("""INSERT INTO `mcx_update_history` (`mcx_update_id`, `as_on`, `count_of_products`)
            VALUES (NULL, %s, %s)""", (data['Summary']['AsOn'], data['Summary']['Count']))
    except Exception as e:
        print(traceback.format_exc())
    return data

get_spot_rates()
