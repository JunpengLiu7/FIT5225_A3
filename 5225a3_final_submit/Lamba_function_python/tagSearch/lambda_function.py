import json
import boto3
from urllib.parse import urlparse, urlunparse

dynamodb = boto3.client('dynamodb')
s3_client = boto3.client('s3')

def validate_input(username, tags):
    if not username or not tags:
        return False, 'Username and tags are required'
    return True, None

def scan_dynamodb_for_keys(username, tags):
    table_name = 'image_tags'
    try:
        response = dynamodb.scan(
            TableName=table_name,
            FilterExpression='username = :username',
            ExpressionAttributeValues={':username': {'S': username}}
        )
        if not response['Items']:
            return [], 'No matching username found'

        return filter_items_by_tags(response['Items'], tags), None
    except dynamodb.exceptions.ResourceNotFoundException:
        return [], 'DynamoDB table not found'
    except Exception as e:
        return [], f'Internal server error: {str(e)}'

def filter_items_by_tags(items, tags):
    image_keys = []
    for item in items:
        if 'tags' in item:
            item_tags = [tag['S'] for tag in item['tags']['L']]
            if all(tag in item_tags for tag in tags):
                image_key = item['key']['S']
                image_keys.append(image_key)
    return image_keys

def generate_clean_presigned_urls(image_keys):
    bucket_name = '5225-a3-images-demo'
    thumbnail_urls = []
    for key in image_keys:
        try:
            # Modify the key to point to the thumbnail version
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
            return [], f'Error generating presigned URL for {thumbnail_key}: {str(e)}'
    return thumbnail_urls, None

def lambda_handler(event, context):
    username = event.get('username')
    tags = event.get('tags')

    is_valid, error_message = validate_input(username, tags)
    if not is_valid:
        return {
            'statusCode': 400,
            'body': json.dumps(error_message)
        }

    tags_list = tags if isinstance(tags, list) else [tags]

    image_keys, error = scan_dynamodb_for_keys(username, tags_list)
    if error:
        status_code = 404 if 'No matching' in error else 500
        return {
            'statusCode': status_code,
            'body': json.dumps(error)
        }

    thumbnail_urls, error = generate_clean_presigned_urls(image_keys)
    if error:
        return {
            'statusCode': 500,
            'body': json.dumps(error)
        }

    return {
        'statusCode': 200,
        'body': json.dumps({'image_urls': thumbnail_urls})
    }
