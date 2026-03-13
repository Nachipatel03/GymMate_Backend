from django.urls import path
from .views import (
    LoginAPIView, MemberRegisterAPIView, NotificationListAPIView, 
    NotificationMarkReadAPIView, NotificationUnreadCountAPIView, 
    AdminProfileAPIView, ChangePasswordAPIView, PasswordResetRequestAPIView,
    PasswordResetConfirmAPIView, EmailTemplateListAPIView, EmailTemplateDetailAPIView
)
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("register/", MemberRegisterAPIView.as_view(), name="register"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("notifications/", NotificationListAPIView.as_view(), name="notifications"),
    path("notifications/unread-count/", NotificationUnreadCountAPIView.as_view(), name="notification-unread-count"),
    path("notifications/<uuid:notification_id>/read/", NotificationMarkReadAPIView.as_view(), name="notification-read"),
    path("admin/profile/", AdminProfileAPIView.as_view(), name="admin-profile"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change-password"),
    path("password-reset/", PasswordResetRequestAPIView.as_view(), name="password-reset"),
    path("password-reset-confirm/", PasswordResetConfirmAPIView.as_view(), name="password-reset-confirm"),
    path("email-templates/", EmailTemplateListAPIView.as_view(), name="email-templates-list"),
    path("email-templates/<slug:slug>/", EmailTemplateDetailAPIView.as_view(), name="email-templates-detail"),
]