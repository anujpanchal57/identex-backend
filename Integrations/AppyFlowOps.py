from pprint import pprint
import boto3 as boto3
from boto3.s3.transfer import S3Transfer
import base64
from utility import conf
from base64 import b64decode
import requests
import json

class AppyFlow:
    def __init__(self, gst_no, secret_key=conf.APPY_FLOW_SECRET_KEY, **kwargs):
        self.__gst_no = gst_no
        self.__secret_key = secret_key

    # For verifying the GST number and if valid then fetching its details
    def get_details(self):
        url = "https://appyflow.in/api/verifyGST?gstNo=" + self.__gst_no + "&key_secret=" + self.__secret_key
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        return response.json()

    # For getting the filing details
    def get_filing_details(self, year):
        url = "https://appyflow.in/api/GST/filing-details"
        payload = {
            "key_secret": self.__secret_key,
            "gstNo": self.__gst_no,
            "year": year
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        return response.json()