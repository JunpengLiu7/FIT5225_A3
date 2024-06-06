import json
import boto3
from urllib.parse import urlparse, urlunparse

s3_client = boto3.client('s3')

def extract_bucket_and_key(url):
    parsed_url = urlparse(url)
    bucket_name = parsed_url.netloc.split('.')[0]
    key = parsed_url.path.lstrip('/')
    return bucket_name, key

def validate_url_structure(key, expected_username):
    path_parts = key.split('/')
    if len(path_parts) < 3 or path_parts[0] != 'images_resized':
        raise ValueError(f"Invalid thumbnail URL structure: {key}")
    if path_parts[1] != expected_username:
        raise ValueError(f"Invalid username in thumbnail URL: {key}")

def generate_presigned_url(bucket_name, key):
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': key},
        ExpiresIn=3600  # URL expiration time in seconds
    )
    parsed_presigned_url = urlparse(presigned_url)
    clean_url = urlunparse((parsed_presigned_url.scheme, parsed_presigned_url.netloc, parsed_presigned_url.path, '', '', ''))
    return clean_url

def generate_fullsize_key(thumbnail_key):
    return thumbnail_key.replace('images_resized', 'images').replace('-thumb', '')

def validate_image_exists(bucket_name, fullsize_key):
    try:
        s3_client.head_object(Bucket=bucket_name, Key=fullsize_key)
        return True
    except s3_client.exceptions.ClientError:
        return False

def process_thumbnail_url(thumbnail_url, expected_username):
    bucket_name, key = extract_bucket_and_key(thumbnail_url)
    validate_url_structure(key, expected_username)
    fullsize_key = generate_fullsize_key(key)
    clean_url = generate_presigned_url(bucket_name, fullsize_key)
    return clean_url, fullsize_key, bucket_name

def lambda_handler(event, context):
    thumbnail_urls = event.get('links')
    expected_username = event.get('username')
    
    if not thumbnail_urls:
        return {
            'statusCode': 400,
            'body': json.dumps('Thumbnail URLs are required')
        }
    
    if not expected_username:
        return {
            'statusCode': 400,
            'body': json.dumps('Username is required')
        }

    fullsize_urls = []
    for url in thumbnail_urls:
        try:
            clean_url, fullsize_key, bucket_name = process_thumbnail_url(url, expected_username)
            if validate_image_exists(bucket_name, fullsize_key):
                fullsize_urls.append(clean_url)
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps(f'Full-size image not found for thumbnail URL: {url}')
                }
        except ValueError as e:
            return {
                'statusCode': 400,
                'body': json.dumps(str(e))
            }
    
    return {
        'statusCode': 200,
        'body': json.dumps({'fullsize_urls': fullsize_urls})
    }
