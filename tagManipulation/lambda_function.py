import json
import boto3
from urllib.parse import urlparse

dynamodb = boto3.client('dynamodb')

def validate_input(urls, operation_type, tags, username):
    if not urls or operation_type is None or not tags or not username:
        return False, 'URLs, type, tags, and username are required'
    return True, None

def extract_key_from_url(url):
    parsed_url = urlparse(url)
    return parsed_url.path.lstrip('/')

def check_user_ownership(key, username):
    return key.startswith(f"images/{username}/")

def query_dynamodb_for_image(table_name, username, key):
    response = dynamodb.scan(
        TableName=table_name,
        FilterExpression='username = :username AND #key = :image_id',
        ExpressionAttributeNames={
            '#key': 'key'
        },
        ExpressionAttributeValues={
            ':username': {'S': username},
            ':image_id': {'S': key}
        }
    )
    return response['Items']

def update_tags(operation_type, current_tags, new_tags):
    current_tags_set = set(current_tags)
    new_tags_set = set(new_tags)

    if operation_type == 1:
        current_tags_set.update(new_tags_set)
    elif operation_type == 0:
        missing_tags = new_tags_set - current_tags_set
        if missing_tags:
            return None, list(missing_tags)
        current_tags_set.difference_update(new_tags_set)

    return list(current_tags_set), None

def update_dynamodb_item(table_name, username, key, tags):
    dynamodb.update_item(
        TableName=table_name,
        Key={
            'username': {'S': username},
            'key': {'S': key}
        },
        UpdateExpression='SET #tags = :tags',
        ExpressionAttributeNames={'#tags': 'tags'},
        ExpressionAttributeValues={':tags': {'L': [{'S': tag} for tag in tags]}}
    )

def lambda_handler(event, context):
    urls = event.get('url')
    operation_type = event.get('type')
    tags = event.get('tags')
    username = event.get('username')
    
    is_valid, error_message = validate_input(urls, operation_type, tags, username)
    if not is_valid:
        return {
            'statusCode': 400,
            'body': json.dumps(error_message)
        }
    
    if isinstance(tags, str):
        tags = [tags]
    
    table_name = 'image_tags'
    errors = []

    for url in urls:
        key = extract_key_from_url(url)
        
        if not check_user_ownership(key, username):
            errors.append(f'The URL does not belong to the user {username}')
            continue
        
        items = query_dynamodb_for_image(table_name, username, key)
        if not items:
            continue
        
        item = items[0]
        current_tags = [tag['S'] for tag in item.get('tags', {}).get('L', [])]
        
        updated_tags, missing_tags = update_tags(operation_type, current_tags, tags)
        if missing_tags:
            errors.append(f'Tag(s) {missing_tags} not inside tag list for the picture {key}')
            continue
        
        update_dynamodb_item(table_name, username, key, updated_tags)
    
    if errors:
        return {
            'statusCode': 400,
            'body': json.dumps(errors)
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps('Tags updated successfully')
    }
