from pprint import pprint
import boto3 as boto3
from boto3.s3.transfer import S3Transfer
import base64
from utility import conf
from base64 import b64decode

class AWS:
    def __init__(self, client, access_key=conf.aws['access_key'], secret_key=conf.aws['secret_key'], **kwargs):
        if client.lower() == "s3":
            self.__aws_client = boto3.client('s3', aws_access_key_id=conf.aws['access_key'],
                                             aws_secret_access_key=conf.aws['secret_key'])
            self.__aws_access_key = access_key
            self.__aws_secret_key = secret_key
            self.__transfer = S3Transfer(self.__aws_client)
            self.__resource = boto3.resource(client)

    ## FOR UPLOADING A FILE ON S3 BUCKET
    def upload_files(self, path, path_in_aws, bucket_name = conf.aws['bucket_name']['uploads']):
        self.__transfer.upload_file(path, bucket_name, path_in_aws)
        return self.__aws_client.put_object_acl(ACL='public-read', Bucket=bucket_name, Key=path_in_aws)

    ## FOR FETCHING THE URL OF THE UPLOADED FILE
    def get_url_of_file(self, key, bucket = conf.aws['bucket_name']['uploads']):
        bucket_location = self.__aws_client.get_bucket_location(Bucket=bucket)
        url = "https://{1}.s3.{0}.amazonaws.com/{2}".format(bucket_location['LocationConstraint'], bucket, key)
        url = url.replace(" ", "+")
        return url

    ## FOR UPLOADING A FILE FROM RAW CONTENT
    def upload_file_from_content(self, data, key, bucket = conf.aws['bucket_name']['uploads']):
        return self.__aws_client.put_object(ACL='public-read', Body=data, Bucket=bucket, Key=key)

    ## FOR UPLOADING A FILE FROM BASE64 CONTENT
    def upload_file_from_base64(self, base64_string, path, bucket=conf.aws['bucket_name']['uploads']):
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        response = self.__resource.Object(bucket, path).put(Body=base64.b64decode(base64_string))
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return self.get_url_of_file(key=path)

# aws = AWS('s3')
# path = "/home/anuj/Downloads/Container Tracking Sheet Updated.xlsx"
# pprint(aws.upload_files(path=path, path_in_aws="B1001/jhbaskhascbsdffdsfc.xlsx"))
# pprint(aws.get_url_of_file(key="B1001/jhbaskhascbfdsfc.xlsx"))
# pprint(aws.upload_file_from_base64(base64_string=base64_str, path="test_uploads/akdhcbdksjfcbhsgfv.png"))