from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.exceptions import AuthenticationFailed


class JWTCookieAuthentication(JWTAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('access_token')
        if not token:
            return None
        try:
            validated = self.get_validated_token(token)
            user = self.get_user(validated)
            return (user, validated)
        except (TokenError, InvalidToken) as e:
            raise AuthenticationFailed(str(e))
