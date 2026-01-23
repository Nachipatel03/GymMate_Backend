from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.hashers import make_password
from accounts.models import Member
from accounts.models import CustomUser,MembershipPlan,Trainer





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
        required=True
    )

    assigned_trainer = serializers.PrimaryKeyRelatedField(
        queryset=Trainer.objects.all(),
        required=False,
        allow_null=True
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

            # ✅ ONLY keep this
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

    assigned_trainer_id = serializers.UUIDField(
        source="assigned_trainer.id",
        read_only=True,
        allow_null=True
    )
    assigned_trainer_name = serializers.CharField(
        source="assigned_trainer.full_name",
        read_only=True
    )

    membership_plan_name = serializers.CharField(
        source="membership_plan.name",
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

            # 👇 trainer fields
            "assigned_trainer_id",
            "assigned_trainer_name",
            "membership_plan_id",
            "membership_plan_name",
            "membership_start",
            "membership_end",
            "status",
            "goal",
            "height",
            "weight",
            "created_at",
        ]
        
class MemberAdminUpdateSerializer(serializers.ModelSerializer):
    assigned_membership = serializers.PrimaryKeyRelatedField(
        queryset=MembershipPlan.objects.all(),
        write_only=True,
        required=False
    )

    assigned_trainer = serializers.PrimaryKeyRelatedField(
        queryset=Trainer.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Member
        fields = [
            "assigned_trainer",
            "assigned_membership",
            "status",
            "goal",
        ]
    def update(self, instance, validated_data):
        # 🔑 mapped field
        membership_plan = validated_data.pop("assigned_membership", None)

        # 🔑 direct FK
        assigned_trainer = validated_data.pop("assigned_trainer", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if membership_plan is not None:
            instance.membership_plan = membership_plan

        if assigned_trainer is not None:
            instance.assigned_trainer = assigned_trainer

        instance.save()
        return instance