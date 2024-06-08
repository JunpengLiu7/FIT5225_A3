import json
import os
from object_detection import detection
import boto3
import base64
import logging

# Initialize clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client("sns")

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = "image_tags"
TOPIC = "arn:aws:sns:us-east-1:796814325471:FIT5225"

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    for item in event["Records"]:
        bucket = item['s3']['bucket']['name']
        key = item['s3']['object']['key']
        logger.info("Processing object from bucket: %s, key: %s", bucket, key)
        
        try:
            upload_image = s3.get_object(Bucket=bucket, Key=key)
            logger.info("Successfully fetched image from S3")
        except Exception as e:
            logger.error("Error fetching image from S3: %s", str(e))
            return {
                'statusCode': 500,
                'body': json.dumps('Error fetching image from S3')
            }
        
        try:
            logger.info('Processing image for detection')
            tags = detection(upload_image['Body'].read())
            logger.info("Detected tags: %s", tags)
        except Exception as e:
            logger.error("Error in object detection: %s", str(e))
            return {
                'statusCode': 500,
                'body': json.dumps('Error in object detection')
            }
        
        table = dynamodb.Table(TABLE_NAME)
        key_parts = key.split("/")
        username = key_parts[1]
        
        try:
            response = table.put_item(Item={
                "username": username,
                "key": key,
                "tags": tags
            })
            logger.info("Successfully inserted item into DynamoDB: %s", response)
        except Exception as e:
            logger.error("Error inserting item into DynamoDB: %s", str(e))
            return {
                'statusCode': 500,
                'body': json.dumps('Error inserting item into DynamoDB')
            }
        print('tags',tags, type(tags))
        message = f"{username} uploaded image with tags {', '.join(tags)}"
        for tag in tags:
            try:
                print('username',username)
                print('tag',tag)
                result = sns_client.publish(
                    TopicArn = TOPIC,
                    Message = message,
                    Subject = "New Image Uploaded",
                    MessageAttributes = {
                        'username': {
                            'DataType': 'String',
                            'StringValue': username
                        },
                        'tags': {
                            'DataType': 'String',
                            'StringValue': tag
                        }
                    }
                )
                if result['ResponseMetadata']['HTTPStatusCode']==200:
                    print(result)
                else:
                    print('e')
                logger.info('Successfully sent SNS message for tag %s for image %s', tag, key)
                
            except Exception as e:
                logger.error('Error publishing SNS message for tag %s: %s', tag, str(e))
    
