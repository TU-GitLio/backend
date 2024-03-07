import logging
import boto3
from botocore.exceptions import ClientError
import os

s3 = boto3.client('s3')


def upload_file_to_s3(file_name, object_name): 
    try:
        s3.upload_file(file_name, 'gitlio', object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True