from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.hashers import make_password
from accounts.models import Member,Notification
from accounts.models import CustomUser,MembershipPlan,Trainer,WorkoutPlan,DietPlan
from django.db import transaction, IntegrityError
from rest_framework.exceptions import ValidationError
from accounts.services.membership_service import MembershipService

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
        value = value.lower().strip()

        existing_user = CustomUser.objects.filter(email=value).first()

        if existing_user and existing_user.is_active:
            raise serializers.ValidationError("This email is already registered.")

        return value

    def create(self, validated_data):
        email = validated_data.pop("email").lower().strip()
        password = validated_data.pop("password")

        with transaction.atomic():

            existing_user = CustomUser.objects.filter(email=email).first()

            if existing_user:
                if existing_user.is_active is False:
                    # ✅ Reactivate old account
                    existing_user.is_active = False   # keep not active until admin approval
                    existing_user.is_verified = False
                    existing_user.password = make_password(password)
                    existing_user.save()

                    member = Member.objects.filter(user=existing_user).first()

                    if member:
                        member.is_deleted = False
                        member.assigned_trainer = None  # ✅ Clear old trainer on re-registration
                        for key, value in validated_data.items():
                            setattr(member, key, value)
                        member.save()

                    # 🔔 Notify admins about re-registration
                    MembershipService.notify_admins(
                        title="Re-Registration Request",
                        message=f"{existing_user.username or member.full_name} ({existing_user.email}) has re-registered and is awaiting admin approval."
                    )

                    return member
                else:
                    raise serializers.ValidationError("Email already exists.")

            # ✅ If no user exists → create fresh
            user = CustomUser.objects.create(
                email=email,
                role="MEMBER",
                is_active=False,
                is_verified=False,
                password=make_password(password),
            )

            member = Member.objects.create(
                user=user,
                email=email,
                **validated_data
            )

            # 🔔 Notify admins about new registration
            MembershipService.notify_admins(
                title="New Member Registration",
                message=f"{member.full_name} ({email}) has registered and is awaiting admin approval."
            )

            return member

class MemberAdminCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)

    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=MembershipPlan.objects.all(),
        required=False,
        write_only=True
    )

    assigned_trainer = serializers.PrimaryKeyRelatedField(
        queryset=Trainer.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Member
        fields = [
            "email",
            "full_name",
            "phone",
            "avatar_url",
            "assigned_trainer",
            "plan_id",
            "status",
            "goal",
            "height",
            "weight",
        ]
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User with this email already exists."
            )
        return value

    def validate_phone(self, value):
        if Member.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "Member with this phone already exists."
            )
        return value
    
    def create(self, validated_data):
        from accounts.services.membership_service import MembershipService

        email = validated_data.pop("email")
        plan = validated_data.pop("plan_id", None)

        DEFAULT_PASSWORD = "@Nick0314"

        with transaction.atomic():
            user = CustomUser.objects.create(
                email=email,
                role="MEMBER",
                is_active=True,
                is_verified=True,
                password=make_password(DEFAULT_PASSWORD),
            )

            member = Member.objects.create(
                user=user,
                email=email,
                **validated_data
            )

            # ✅ Activate membership if plan selected
            if plan:
                MembershipService.activate_membership(
                    member=member,
                    plan=plan,
                    payment_method="cash"
                )

        return member


class MemberWorkoutPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutPlan
        fields = ["id", "name", "status", "start_date", "end_date"]
        
class MemberDietPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietPlan
        fields = ["id", "name", "status"]
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

    join_date = serializers.DateTimeField(
    source="created_at",
    format="%Y-%m-%d",
    read_only=True
)
    active_membership = serializers.SerializerMethodField()
    
    workout_plans = MemberWorkoutPlanSerializer(
        many=True,
        read_only=True
    )

    diet_plans = MemberDietPlanSerializer(
        many=True,
        read_only=True
    )
    
    can_change_plan = serializers.SerializerMethodField()


    class Meta:
        model = Member
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "status",
            "goal",
            "can_change_plan",
            "assigned_trainer_id",      # ✅ MUST BE HERE
            "assigned_trainer_name",    # ✅ MUST BE HERE
            "join_date",                # ✅ MUST BE HERE
            "active_membership",
            "workout_plans",   
            "diet_plans",
            
        ]
    def get_can_change_plan(self, obj):
        active_membership = obj.memberships.filter(status="active").exists()
        return not active_membership
    
    def get_active_membership(self, obj):
        membership = obj.memberships.filter(status="active").first()
        if not membership:
            return None

        return {
            "plan_id": membership.plan.id,
            "plan_name": membership.plan.name,
            "start_date": membership.start_date,
            "end_date": membership.end_date,
            "status": membership.status
        }

        
from accounts.services.membership_service import MembershipService

class MemberAdminUpdateSerializer(serializers.ModelSerializer):

    plan_id = serializers.PrimaryKeyRelatedField(
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
            "plan_id",
            "status",
            "goal",
        ]
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User with this email already exists."
            )
        return value

    def validate_phone(self, value):
        if Member.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "Member with this phone already exists."
            )
        return value
    
    def update(self, instance, validated_data):

        # Update trainer (even if null)
        if "assigned_trainer" in validated_data:
            instance.assigned_trainer = validated_data.get("assigned_trainer")

        # Update normal fields
        if "status" in validated_data:
            instance.status = validated_data.get("status")

        if "goal" in validated_data:
            instance.goal = validated_data.get("goal")

        # Handle membership change
        
        # if "plan_id" in validated_data:
        #     plan = validated_data.get("plan_id")
        #     if plan:
        #         MembershipService.activate_membership(
        #             member=instance,
        #             plan=plan,
        #             payment_method="cash"
        #         )

        instance.save()
        return instance
