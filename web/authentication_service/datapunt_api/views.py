from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework_jwt.settings import api_settings
from rest_framework.views import APIView
from rest_framework.response import Response


def cleanup_payload(payload):
    """
    remove deprecated keys from payload,
        see rest_framwework_jwt.utils.jwt_payload_handler version 1.8.0, which is putting them in
    """
    return {k: v for (k,v) in payload.items() if k != 'email' and k != 'user_id'}


class AuthenticationTokenView(APIView):
    def post(self, request):
        token = None
        if 'username' in request.data and 'password' in request.data:
            token = self.grant_user_credentials(request)

        if 'pid' in request.data and 'creds' in request.data:
            token = self.grant_siam(request)

        if token is not None:
            return Response({'token': token})

        return Response({"non_field_errors": ["Unable to login with provided credentials."]},
                        status=status.HTTP_400_BAD_REQUEST)

    def grant_user_credentials(self, request):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = cleanup_payload(jwt_payload_handler(user))
            payload['grant_type'] = 'user_credentials'

            return jwt_encode_handler(payload)

        return None

    def grant_siam(self, request):
        return None


class SamlTokenView(APIView):
    def get(self, request):
        return Response({'saml': request.META['x-saml-attribute-token1']})
