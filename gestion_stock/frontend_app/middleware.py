from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model

User = get_user_model()


class JWTCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            token = request.COOKIES.get('access_token')
            if token:
                try:
                    payload = AccessToken(token)
                    user = User.objects.get(id=payload['user_id'])
                    request.user = user
                except (TokenError, User.DoesNotExist):
                    pass
        return self.get_response(request)
