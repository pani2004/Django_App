from datetime import timedelta

from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserSerializer


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)

        access = resp.data.get("access")
        refresh = resp.data.get("refresh")
        if access:
            access_lifetime = settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME", timedelta(hours=8))
            max_age = int(access_lifetime.total_seconds())
            resp.set_cookie(
                "access",
                access,
                max_age=max_age,
                httponly=True,
                samesite="Lax",
                secure=request.is_secure(),
                path="/",
            )
        if refresh:
            refresh_lifetime = settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME", timedelta(days=7))
            max_age = int(refresh_lifetime.total_seconds())
            resp.set_cookie(
                "refresh",
                refresh,
                max_age=max_age,
                httponly=True,
                samesite="Lax",
                secure=request.is_secure(),
                path="/",
            )

        return resp


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        resp = Response({"detail": "logged out"}, status=status.HTTP_200_OK)
        resp.delete_cookie("access", path="/")
        resp.delete_cookie("refresh", path="/")
        return resp


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
