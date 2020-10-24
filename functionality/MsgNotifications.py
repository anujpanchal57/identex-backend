# import boto3
# from utility import conf
# sns = boto3.client("sns",
#     aws_access_key_id=conf.aws['access_key'],
#     aws_secret_access_key=conf.aws['secret_key'],
#     region_name="ap-south-1")
# number = '+919920773997'
# print(sns.publish(PhoneNumber=number, Message='example text message'))