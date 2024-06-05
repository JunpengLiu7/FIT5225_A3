from django.shortcuts import render, redirect
from django import template
from webpage import decode_jwt
# from decouple import config
import boto3
import os
import base64
import requests
from django.http import HttpResponse



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
    # env paras
    REDIRECT_URL = 'http://localhost:8000'
    TOKEN_ENDPOINT = 'https://5225a3test.auth.us-east-1.amazoncognito.com/oauth2/token'
    #TOKEN_ENDPOINT = 'https://5225a3test1.auth.us-east-1.amazoncognito.com/oauth2/token'

    CLIENT_ID = '1mc2fqr6eho90ak0tajeuv55gq'
    #CLIENT_ID = '3em6frsfg726bkb5kkbgn17l4r'
    USER_POOL_ID = 'us-east-1_c63xLDbhq'
    #USER_POOL_ID = 'us-east-1_wMgJLv0Az'
    # CLIENT_SECRET = 'qkdpl928cducncnu5ib551vkcs2cojn2lm6cer79utenu64nmhk'
    COGNITO_REGION_NAME = 'us-east-1'
    username = 'xiaonanli'
    password = 'xiao315341583A!'

    # TOKEN_ENDPOINT = config('TOKEN_ENDPOINT')
    # REDIRECT_URL = config('REDIRECT_URL')
    # CLIENT_ID = config('CLIENT_ID')
    # USER_POOL_ID = config('USER_POOL_ID')
    # TOKEN_ENDPOINT = os.getenv('TOKEN_ENDPOINT')
    # REDIRECT_URL = os.getenv('REDIRECT_URL')
    # CLIENT_ID = os.getenv('CLIENT_ID')
    # USER_POOL_ID = os.getenv('USER_POOL_ID')
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
    print(id_token)

    new_response = cog_client.get_user(
        AccessToken=access_token
    )
    print(new_response)

    user_email = None
    for attr in new_response['UserAttributes']:
        if attr['Name'] == 'email':
            user_email = attr['Value']
            break

    user_email = None
    for attr in new_response['UserAttributes']:
        if attr['Name'] == 'email':
            user_email = attr['Value']
            break
            
    user_email = None
    for attr in new_response['UserAttributes']:
        if attr['Name'] == 'email':
            user_email = attr['Value']
            break


def convert_image_to_base64(image_file):
    with open(image_file, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")
    return image_base64

access_token = 'eyJraWQiOiJhVVNWbGFtUFdsaHFDbFZ4SGNXQnBpZndZV2c5NzJsVjJjOFJmRXBDTGpNPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJiNDM4YjQyOC00MDMxLTcwOGMtY2EwNy1jNWZmNjI4NzU5MzUiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfYzYzeExEYmhxIiwiY29nbml0bzp1c2VybmFtZSI6InhpYW9uYW5saSIsImdpdmVuX25hbWUiOiJ4aWFvbmFuIiwib3JpZ2luX2p0aSI6Ijk1MTRiMmY4LTlkMWQtNDFmNy1iMDYwLTc0YWY4ODdlOWQ0NiIsImF1ZCI6IjFtYzJmcXI2ZWhvOTBhazB0YWpldXY1NWdxIiwiZXZlbnRfaWQiOiJiZGRhM2ZlMS1iZTZkLTQ0NWItOTc2Yy1lNWNjYmUxZDQzOWIiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcxNzU3MTA4OCwiZXhwIjoxNzE3NjU3NDg4LCJpYXQiOjE3MTc1NzEwODgsImZhbWlseV9uYW1lIjoibGkiLCJqdGkiOiI3MzYxZGY5OS0wOGQyLTRhMDUtYWIyMi1kMWRiNmEwZDM2ZDciLCJlbWFpbCI6ImFsZXgueGlhb25hbkBnbWFpbC5jb20ifQ.c4L7UvDemvVhQ9Y4pF-S46E7pGfgG7EGJ50BqgOEhIwSFVd7PBtUUnJs20gp17C-nm7j0yHf7te8PeP4VVyEKxN6a5vmEaFl1hKWA6iJkrXPiU_MA0hsH90Wljb3hpXekyptirks3KFFHuaF0RP_KuNBaar5O7xLbAB0T0olQk0la6_7-7QOrVpzsX9KglWQrf1VDzQzM3sX8UKFdS18aB6MUhJdYcSBOf_6SWAHXlmfsL_IIYGbZTVqYU-COktpzcwleUVkgQCb37qSxiej9A9mJE-Z_w7F-Qc9tICL6dnJplMXwUtDHZihne6dD_X506Tz3vfWOliaTPyoELfcTQ'

def upload_image_to_api_gateway(username, image_name, base64_image, api_endpoint, access_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "username": username,
        "image_name": image_name,
        "image_file": base64_image
    }
    response = requests.post(api_endpoint, headers=headers, json=data)
    return response.status_code, response.text

def upload_image(request):
    if request.method == "POST":
        username = request.POST["username"]
        print(username)
        image_name = request.FILES["image"].name
        image_file = request.FILES["image"]
        token = access_token
        base64_image = convert_image_to_base64(image_file)
        status_code, response_text = upload_image_to_api_gateway(username, image_name, base64_image, "https://5225a3test.auth.us-east-1.amazoncognito.com/oauth2/authorize?client_id=1mc2fqr6eho90ak0tajeuv55gq&response_type=token&scope=email+openid+profile&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fhome1%2F", token)
        # Handle the response from the API gateway
        return HttpResponse(f"Status code: {status_code}, Response: {response_text}")
    return render(request, "upload_image.html")

    # code = request.GET.get('code')
    # userData = getTokens(code)
    # return render(request, 'home.html')

    