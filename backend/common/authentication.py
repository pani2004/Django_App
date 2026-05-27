from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """
    Authenticate using JWTs stored in HttpOnly cookies.
    """

    access_cookie_name = "access"

    def authenticate(self, request):
        raw_token = request.COOKIES.get(self.access_cookie_name)
        if not raw_token:
            return super().authenticate(request)

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        return user, validated_token

