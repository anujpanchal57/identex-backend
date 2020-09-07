import json
import re
from pprint import pprint

import requests
from bs4 import BeautifulSoup

spot_url = "https://www.mcxindia.com/market-data/spot-market-price"


def get_spot_rates():
    page_source = BeautifulSoup(requests.get(spot_url).text).find_all("script")[4].string.replace("//<![CDATA[","").replace(";//]]>","").replace("var vSMP=","").strip()
    data = json.loads(page_source.split(';')[0])
    count = 0
    for spot_rate in data['Data']:
        spot_rate['Date'] = int(spot_rate['Date'].replace('/Date(','').replace(')/',''))
        data['Data'][count] = spot_rate
    data['Summary']['AsOn'] = int(data['Summary']['AsOn'].replace('/Date(','').replace(')/',''))
    return data
