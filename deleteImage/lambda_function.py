import json
import boto3
from urllib.parse import urlparse

s3_client = boto3.client('s3')
dynamodb = boto3.client('dynamodb')

def validate_input(urls, username):
    if not urls or not username:
        return False, 'URLs and username are required'
    return True, None

def parse_url(url):
    parsed_url = urlparse(url)
    key = parsed_url.path.lstrip('/')
    return key

def s3_object_exists(bucket_name, key):
    try:
        s3_client.head_object(Bucket=bucket_name, Key=key)
        return True
    except s3_client.exceptions.ClientError:
        return False

def delete_s3_objects(bucket_name, key):
    image_exists = s3_object_exists(bucket_name, key)
    if image_exists:
        s3_client.delete_object(Bucket=bucket_name, Key=key)
    else:
        raise Exception(f"S3 object {key} does not exist")
    
    thumbnail_key = key.replace('.jpg', '-thumb.jpg')
    if s3_object_exists(bucket_name, thumbnail_key):
        s3_client.delete_object(Bucket=bucket_name, Key=thumbnail_key)

def delete_dynamodb_item(table_name, username, key):
    try:
        dynamodb.delete_item(
            TableName=table_name,
            Key={
                'username': {'S': username},
                'key': {'S': key}
            },
            ConditionExpression="#u = :username AND #k = :key",
            ExpressionAttributeNames={
                '#u': 'username',
                '#k': 'key'
            },
            ExpressionAttributeValues={
                ':username': {'S': username},
                ':key': {'S': key}
            }
        )
    except dynamodb.exceptions.ConditionalCheckFailedException:
        pass  # Item does not exist, which is okay in this context

def lambda_handler(event, context):
    urls = event.get('url')
    username = event.get('username')
    
    is_valid, error_message = validate_input(urls, username)
    if not is_valid:
        return {
            'statusCode': 400,
            'body': json.dumps(error_message)
        }
    
    table_name = 'image_tags'
    bucket_name = '5225-a3-images-demo'
    errors = []
    
    for url in urls:
        key = parse_url(url)
        
        if not key.startswith(f"images/{username}/"):
            errors.append(f'The URL {url} does not belong to the user {username}')
            continue
        
        try:
            delete_s3_objects(bucket_name, key)
            delete_dynamodb_item(table_name, username, key)
        except Exception as e:
            errors.append(f'Error processing {url}: {str(e)}')
    
    if errors:
        return {
            'statusCode': 500,
            'body': json.dumps(errors)
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps('Images deleted successfully')
    }
