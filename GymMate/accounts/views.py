from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from members.serializers import MemberRegisterSerializer
from accounts.models import Notification
from accounts.serializers import NotificationSerializer

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
                "message": "Registration successful. Please wait for verification.",
                "member_id": member.id,
                "email": member.user.email,
                "is_verified": member.user.is_verified,
            },
            status=status.HTTP_201_CREATED
        )

class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # 🛡 Admin sees ALL notifications
        if request.user.role == "ADMIN":
            notifications = Notification.objects.filter( type="admin").order_by("-created_at")

        # 👤 Member sees only their own
        else:
            notifications = Notification.objects.filter(
                user=request.user,
            ).order_by("-created_at")

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
class NotificationMarkReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, notification_id):

        # 🛡 Admin can mark any notification
        if request.user.role == "ADMIN":
            notification = get_object_or_404(
                Notification,
                id=notification_id,
                type="admin",
                is_read=False
            )

        # 👤 Member / Trainer can only mark their own
        else:
            notification = get_object_or_404(
                Notification,
                id=notification_id,
                user=request.user,
                type=request.user.role,
                is_read=False
            )

        notification.is_read = True
        notification.save()

        return Response(
            {"message": "Notification marked as read"},
            status=status.HTTP_200_OK
        )

    def delete(self, request, notification_id):

        # 🛡 Admin can delete any notification
        if request.user.role == "ADMIN":
            notification = get_object_or_404(
                Notification,
                id=notification_id,
                type="admin"
            )

        # 👤 Member / Trainer can only delete their own
        else:
            notification = get_object_or_404(
                Notification,
                id=notification_id,
                user=request.user,
                type=request.user.role
            )

        notification.delete()

        return Response(
            {"message": "Notification deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

class NotificationUnreadCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role == "ADMIN":
            count = Notification.objects.filter(
                type="admin",
                is_read=False
            ).count()
        else:
            count = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()

        return Response({"unread_count": count})