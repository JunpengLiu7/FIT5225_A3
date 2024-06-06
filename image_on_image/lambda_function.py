import json
import boto3
import base64
import cv2
import numpy as np
from urllib.parse import urlparse, urlunparse
import object_detection  # Assuming this is correctly imported from the object_detection script

dynamodb = boto3.client('dynamodb')
s3_client = boto3.client('s3')

def get_image_keys_by_tags(username, tags):
    table_name = 'image_tags'
    image_keys = []
    try:
        for tag in tags:
            response = dynamodb.scan(
                TableName=table_name,
                FilterExpression='username = :username AND contains(#tags, :tag)',
                ExpressionAttributeNames={'#tags': 'tags'},
                ExpressionAttributeValues={
                    ':username': {'S': username},
                    ':tag': {'S': tag}
                }
            )
            for item in response['Items']:
                image_keys.append(item['key']['S'])

        if not image_keys:
            return [], 'No matching images found for the given tags'
        
        return list(set(image_keys)), None
    except dynamodb.exceptions.ResourceNotFoundException:
        return [], 'DynamoDB table not found'
    except Exception as e:
        return [], f'Internal server error: {str(e)}'

def generate_presigned_urls(image_keys):
    bucket_name = '5225-a3-images-demo'
    thumbnail_urls = []
    
    for key in image_keys:
        try:
            thumbnail_key = key.replace('images/', 'images_resized/').replace('.jpg', '-thumb.jpg')
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': thumbnail_key},
                ExpiresIn=3600  # URL expiration time in seconds
            )
            parsed_url = urlparse(presigned_url)
            clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
            thumbnail_urls.append(clean_url)
        except Exception as e:
            return [], f'Error generating presigned URL for {key}: {str(e)}'
    
    return thumbnail_urls, None

def lambda_handler(event, context):
    try:
        if 'body' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps('Request body is required')
            }
        
        try:
            request_body = json.loads(event['body'])
        except json.JSONDecodeError as e:
            return {
                'statusCode': 400,
                'body': json.dumps('Invalid JSON in request body')
            }

        image_data = request_body.get('body')
        username = request_body.get('username')
        
        if not image_data or not username:
            return {
                'statusCode': 400,
                'body': json.dumps('Username and image data are required')
            }

        try:
            image_bytes = base64.b64decode(image_data)
            detected_tags = object_detection.detection(image_bytes)
            unique_tags = list(set(detected_tags))
            
            if not unique_tags:
                return {
                    'statusCode': 404,
                    'body': json.dumps('No objects detected in the uploaded image')
                }

            image_keys, error = get_image_keys_by_tags(username, unique_tags)
            if error:
                status_code = 404 if 'No matching' in error else 500
                return {
                    'statusCode': status_code,
                    'body': json.dumps(error)
                }

            image_urls, error = generate_presigned_urls(image_keys)
            if error:
                return {
                    'statusCode': 500,
                    'body': json.dumps(error)
                }

            return {
                'statusCode': 200,
                'body': json.dumps({'image_urls': image_urls})
            }

        except (base64.binascii.Error, ValueError) as e:
            return {
                'statusCode': 400,
                'body': json.dumps(f'Invalid image data: {str(e)}')
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Internal server error: {str(e)}')
        }
