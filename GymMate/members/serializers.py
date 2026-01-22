from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.hashers import make_password
from accounts.models import Member
from accounts.models import CustomUser,MembershipPlan





class MemberRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Member
        fields = [
            "email",
            "password",
            "full_name",
            "phone",
        ]
    
    def validate_email(self, value):
        # check in CustomUser
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )

        # optional: double safety if you keep email in Member
        if Member.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "This email is already registered as a member."
            )

        return value

    def create(self, validated_data):
        email = validated_data.pop("email")
        password = validated_data.pop("password")

        with transaction.atomic():
            # 1️⃣ Create user (NOT verified)
            user = CustomUser.objects.create(
                email=email,
                role="MEMBER",
                is_active=True,
                is_verified=False,   # 🔴 IMPORTANT
                password=make_password(password),
            )

            # 2️⃣ Create member profile
            member = Member.objects.create(
                user=user,
                email=email,
                **validated_data
            )

        return member

class MemberAdminCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    assigned_membership = serializers.PrimaryKeyRelatedField(
        source="membership_plan",
        queryset=MembershipPlan.objects.all(),
        required=False
    )

    member_email = serializers.EmailField(
        source="user.email",
        read_only=True
    )

    class Meta:
        model = Member
        fields = [
            "member_email",
            "email",
            "full_name",
            "phone",
            "avatar_url",
            "trainer",
            "assigned_trainer",
            "assigned_membership",
            "membership_start",
            "membership_end",
            "status",
            "goal",
            "height",
            "weight",
        ]

    def create(self, validated_data):
        email = validated_data.pop("email")
        DEFAULT_PASSWORD = "@Nick0314"

        with transaction.atomic():
            # 1️⃣ Create verified user
            user = CustomUser.objects.create(
                email=email,
                role="MEMBER",
                is_active=True,
                is_verified=True,  
                password=make_password(DEFAULT_PASSWORD),
            )

            # 2️⃣ Create member profile
            member = Member.objects.create(
                user=user,
                email=email,
                **validated_data
            )

        return member

class MemberSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    trainer_name = serializers.CharField(
        source="trainer.full_name",
        read_only=True
    )

    class Meta:
        model = Member
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "avatar_url",
            "trainer_name",
            "membership_plan",
            "membership_start",
            "membership_end",
            "status",
            "goal",
            "height",
            "weight",
            "created_at",
        ]