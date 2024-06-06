import json
import boto3

TOPIC = "arn:aws:sns:us-east-1:796814325471:FIT5225"

def lambda_handler(event, context):
    sns_client = boto3.client('sns')
    data = json.loads(event['body'])
    
    email = data['email']
    tag = data['tag']
    username = data['username']
    
    subscription_arn = find_subscription(email, sns_client)
    
    if subscription_arn:
        update_subscription_filter(subscription_arn, tag, sns_client)
        result = f"Subscription updated for {email} with tag {tag}"
    else:
        create_subscription(email, tag, username, sns_client)
        result = f"Subscription created for {email} with tag {tag}"
    
    return {
        'statusCode': 200,
        'body': json.dumps(result),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': '*'
        }
    }

def find_subscription(email, sns_client):
    response = sns_client.list_subscriptions_by_topic(TopicArn=TOPIC)
    for subscription in response['Subscriptions']:
        if subscription['Endpoint'] == email:
            return subscription['SubscriptionArn']
    return None

def update_subscription_filter(subscription_arn, tag, sns_client):
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

def create_subscription(email, tag, username, sns_client):
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
