import json
import os
from object_detection import detection
import boto3
import base64

s3 = boto3.client('s3')
dynamodb =boto3.resource('dynamodb')
TABLE_NAME="image_tags"

def lambda_handler(event, context):
    print(event)
    for item in event["Records"]:
        bucket = item['s3']['bucket']['name']
        key = item['s3']['object']['key']
        upload_image = s3.get_object(Bucket=bucket, Key=key)
        
        print('haha')
        tags = detection(upload_image['Body'].read())
       
        print("tags: {}" .format(tags))
        
        
        table = dynamodb.Table(TABLE_NAME)
        key_parts = key.split("/")
        username = key_parts[1]
        
        print(table.put_item( Item={
            "username":username,
            "key":key,
            "tags":tags
        }))
        
