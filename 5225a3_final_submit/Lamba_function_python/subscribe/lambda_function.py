import json
import boto3
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

TOPIC = "arn:aws:sns:us-east-1:796814325471:FIT5225"

def lambda_handler(event, context):
    sns_client = boto3.client('sns')
    data = json.loads(event['body'])
    email = data['email']
    tag = data['tag']
    username = data['username']
    
    logger.info(f"Received data: email={email}, tag={tag}, username={username}")
    
    subscription_arn = find_subscription(email, sns_client)
    result = ""
    
    if subscription_arn:
        logger.info(f"Found existing subscription: {subscription_arn}")
        response = sns_client.get_subscription_attributes(SubscriptionArn=subscription_arn)
        filter_policy = json.loads(response['Attributes'].get('FilterPolicy', '{}'))
        if 'tag' not in filter_policy:
            filter_policy['tag'] = []
        if tag not in filter_policy['tag']:
            filter_policy['tag'].append(tag)
        sns_client.set_subscription_attributes(
            SubscriptionArn=subscription_arn,
            AttributeName='FilterPolicy',
            AttributeValue=json.dumps(filter_policy)
        )
        result = f'Subscription updated for {email} with tag {tag}'
    else:
        logger.info("No existing subscription found, creating new one")
        sns_client.subscribe(
            TopicArn=TOPIC,
            Protocol='email',
            Endpoint=email,
            Attributes={
                'FilterPolicy': json.dumps({
                    'tag': [tag],
                    'username': [username]
                })
            }
        )
        result = f"Subscription created for {email} with tag {tag}"
        responed = {
            "result":result,
            'code':201
        }
        
    return {
        'statusCode': 200,
        'body': json.dumps(result),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': '*',
        }
    }

def find_subscription(endpoint, sns_client):
    logger.info(f"Finding subscription for endpoint: {endpoint}")
    response = sns_client.list_subscriptions_by_topic(TopicArn=TOPIC)
    for subscription in response['Subscriptions']:
        if subscription['Endpoint'] == endpoint:
            logger.info(f"Subscription found: {subscription['SubscriptionArn']}")
            return subscription['SubscriptionArn']
    logger.info("No subscription found")
    return None