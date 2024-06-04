from rest_framework import authentication, exceptions
from .cognito import verify_cognito_token
from django.conf import settings

class CognitoAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            token = auth_header.split()[1]
            decoded_token = verify_cognito_token(
                token,
                settings.AWS_COGNITO_REGION,
                settings.AWS_COGNITO_USER_POOL_ID,
                settings.AWS_COGNITO_CLIENT_ID
            )
            return (decoded_token, None)
        except Exception as e:
            raise exceptions.AuthenticationFailed('Invalid token')
