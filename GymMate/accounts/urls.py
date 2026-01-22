from django.urls import path
from .views import LoginAPIView,MemberRegisterAPIView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("register/", MemberRegisterAPIView.as_view(), name="register"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]