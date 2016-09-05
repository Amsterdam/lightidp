from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings
from rest_framework.views import APIView
from rest_framework.response import Response



class AuthenticationTokenView(APIView):
    def post(self, request):
        if 'grant_type' in request.data and request.data['grant_type'] == 'password':
            username = request.data['username']
            password = request.data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                request.session['token'] = token

        return self.get(request)

    def get(self, request):
        token = request.session.get('token', None)
        if not token:
            return Response([])

        return Response({'token': token})

