from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from members.serializers import MemberRegisterSerializer
from accounts.models import Notification, CustomUser, EmailTemplate
from accounts.serializers import (
    NotificationSerializer, 
    AdminProfileSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailTemplateSerializer
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from accounts.services.email_service import EmailService
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives

class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class MemberRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MemberRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        member = serializer.save()

        return Response(
            {
                "message": "Registration successful. You can now login.",
                "member_id": member.id,
                "email": member.user.email,
                "is_verified": member.user.is_verified,
            },
            status=status.HTTP_201_CREATED
        )

class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # 🛡 Admin / Member / Trainer sees only their own notifications
        notifications = Notification.objects.filter(
            user=request.user,
        ).order_by("-created_at")

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
class NotificationMarkReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, notification_id):

        # 🛡 Admin / Member / Trainer can only mark their own
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            user=request.user
        )

        notification.is_read = True
        notification.save()

        return Response(
            {"message": "Notification marked as read"},
            status=status.HTTP_200_OK
        )

    def delete(self, request, notification_id):

        # 🛡 Admin / Member / Trainer can only delete their own
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            user=request.user
        )

        notification.delete()

        return Response(
            {"message": "Notification deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

class NotificationMarkAllReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return Response(
            {"message": "All notifications marked as read"},
            status=status.HTTP_200_OK
        )

class NotificationUnreadCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return Response({"unread_count": count})

class AdminProfileAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        serializer = AdminProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = AdminProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

class PasswordResetRequestAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = CustomUser.objects.filter(email=email).first()
        
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Use frontend URL from settings if available, else localhost
            # frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
            frontend_url = getattr(settings, 'FRONTEND_URL', 'https://gymmate-uz2j.onrender.com')
            reset_link = f"{frontend_url}/reset-password-confirm/{uid}/{token}/"
            
            context = {
                'user': user,
                'reset_link': reset_link,
                'SupportEmail': getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@gymmate.com'),
                'Year': 2026 # Should ideally be dynamic
            }
            
            # Try loading from database first
            from accounts.services.email_service import get_template_from_db
            db_subject, db_html = get_template_from_db('password_reset')
            if db_html:
                from django.template import Template, Context
                html_content = Template(db_html).render(Context(context))
                subject = db_subject or "GymMate - Password Reset Request"
            else:
                html_content = render_to_string('emails/password_reset_email.html', context)
                subject = "GymMate - Password Reset Request"

            text_content = strip_tags(html_content)
            
            email_msg = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            email_msg.attach_alternative(html_content, "text/html")
            email_msg.send()
            
        # Always return 200 to prevent email harvesting
        return Response({"message": "If an account exists with this email, a reset link has been sent."}, status=status.HTTP_200_OK)

class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None
            
        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "The reset link is invalid or has expired."}, status=status.HTTP_400_BAD_REQUEST)

class EmailTemplateListAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        templates = EmailTemplate.objects.all().order_by('name')
        serializer = EmailTemplateSerializer(templates, many=True)
        return Response(serializer.data)

class EmailTemplateDetailAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, slug):
        template = get_object_or_404(EmailTemplate, slug=slug)
        serializer = EmailTemplateSerializer(template)
        return Response(serializer.data)

    def patch(self, request, slug):
        template = get_object_or_404(EmailTemplate, slug=slug)
        serializer = EmailTemplateSerializer(template, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
