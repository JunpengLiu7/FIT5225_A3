import requests
from jose import jwt

def get_cognito_public_keys(region, user_pool_id):
    url = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
    response = requests.get(url)
    keys = response.json()['keys']
    return keys

def verify_cognito_token(token, region, user_pool_id, app_client_id):
    keys = get_cognito_public_keys(region, user_pool_id)
    header = jwt.get_unverified_header(token)
    key = next(k for k in keys if k['kid'] == header['kid'])

    try:
        verified_token = jwt.decode(token, key, algorithms=['RS256'], audience=app_client_id)
        return verified_token
    except jwt.ExpiredSignatureError:
        raise Exception('Token expired')
    except jwt.JWTClaimsError:
        raise Exception('Invalid claims')
    except Exception:
        raise Exception('Invalid token')
