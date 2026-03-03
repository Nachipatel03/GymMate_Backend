from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models import Notification
from rest_framework import serializers
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # ✅ Add custom claims
        token["role"] = user.role
        token["email"] = user.email

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # ✅ Send user info with token
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "role": self.user.role,
            "username": self.user.username,
            
        }
        return data
    
class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "is_read",
            "created_at",
        ]
        read_only_fields = fields
