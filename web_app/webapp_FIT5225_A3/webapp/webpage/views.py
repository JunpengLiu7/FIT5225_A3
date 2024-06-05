from django.shortcuts import render, redirect
from django import template
from webpage import decode_jwt
from decouple import config
import boto3
import os
import base64
import requests



# def getTokens(code):
#     TOKEN_ENDPOINT = config('TOKEN_ENDPOINT')
#     REDIRECT_URL = config('REDIRECT_URL')
#     CLIENT_ID = config('CLIENT_ID')
#     CLIENT_SECRET = config('CLIENT_SECRET')

#     encodeData = base64.b64encode(bytes(f"{CLIENT_ID}:{CLIENT_SECRET}", "ISO-8859-1")).decode("ascii")

#     hearders = {
#         'Content-Type': 'application/x-www-from-urlencoded',
#         'Authorization': f'Basic{encodeData}'
#     }

#     body = {
#         'grant_type': 'authorization_code',
#         'client_id': CLIENT_ID,
#         'code': code,
#         'redirect_url': REDIRECT_URL
#     }

#     response = requests.post(TOKEN_ENDPOINT, data=body, headers=hearders)
    

#     id_token = response.json()

#     decode_jwt.lambda_handler(id_token)

def home(request):
    username = 'xiaonanli'
    password = 'xiao315341583A!'

    TOKEN_ENDPOINT = config('TOKEN_ENDPOINT')
    REDIRECT_URL = config('REDIRECT_URL')
    CLIENT_ID = config('CLIENT_ID')
    USER_POOL_ID = config('USER_POOL_ID')
    #CLIENT_SECRET = config('CLIENT_SECRET')

    cog_client = boto3.client('cognito-idp', region_name='us-east-1')
    response = cog_client.initiate_auth(
        #UserPoolId=USER_POOL_ID,
        ClientId=CLIENT_ID,
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password
    })
    
    access_token = response['AuthenticationResult']['AccessToken']
    refresh_token = response['AuthenticationResult']['RefreshToken']
    id_token = response['AuthenticationResult']['IdToken']

    new_response = cog_client.get_user(
        AccessToken=access_token
    )
    print(new_response)

    user_email = None
    for attr in new_response['UserAttributes']
        if attr['Name'] == 'email':
            user_email = attr['Value']
            break

    user_email = None
    for attr in new_response['UserAttributes']
        if attr['Name'] == 'email':
            user_email = attr['Value']
            break
            
    user_email = None
    for attr in new_response['UserAttributes']
        if attr['Name'] == 'email':
            user_email = attr['Value']
            break

    # code = request.GET.get('code')
    # userData = getTokens(code)
    # return render(request, 'home.html')

    