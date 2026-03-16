from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models import Notification, CustomUser, EmailTemplate
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
        ]
        read_only_fields = fields

class AdminProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='username')

    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'email', 'phone']
        read_only_fields = ['id', 'email']  # Prevent changing email for security if needed, or allow it

    def update(self, instance, validated_data):
        if 'username' in validated_data:
            instance.username = validated_data['username']
        
        if 'phone' in validated_data:
            instance.phone = validated_data['phone']
        
        # Optional: if allowing email updates
        if 'email' in validated_data:
            instance.email = validated_data['email']

        instance.save()
        return instance

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ['id', 'slug', 'name', 'subject', 'html_body', 'updated_at']
        read_only_fields = ['id', 'slug', 'updated_at']
