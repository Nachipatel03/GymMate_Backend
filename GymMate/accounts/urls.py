from django.urls import path
from .views import LoginAPIView,MemberRegisterAPIView,NotificationListAPIView,NotificationMarkReadAPIView, NotificationUnreadCountAPIView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("register/", MemberRegisterAPIView.as_view(), name="register"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("notifications/", NotificationListAPIView.as_view(), name="notifications"),
    path("notifications/unread-count/", NotificationUnreadCountAPIView.as_view(), name="notification-unread-count"),
    path("notifications/<uuid:notification_id>/read/", NotificationMarkReadAPIView.as_view(), name="notification-read"),
]