from django.utils import timezone
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.db.models import Sum
from accounts.models import (
    Member, Notification, Payment, MemberProgress,
    CustomUser, MembershipPlan, Trainer, WorkoutPlan
)
from diets.models import DietPlan
import logging

logger = logging.getLogger(__name__)

class MemberProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberProgress
        fields = ["id", "date", "weight", "body_fat", "muscle_mass", "measurements", "notes"]
        read_only_fields = ["id"]
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
                    # ✅ Reactivate old account and allow immediate login
                    existing_user.is_active = True
                    existing_user.is_verified = True
                    existing_user.password = make_password(password)
                    existing_user.save()

                    member = Member.objects.filter(user=existing_user).first()

                    if member:
                        member.is_deleted = False
                        member.assigned_trainer = None  # ✅ Clear old trainer on re-registration
                        member.created_at = timezone.now() # ✅ Reset join date to today
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

            # ✅ If no user exists → create fresh and allow immediate login
            user = CustomUser.objects.create(
                email=email,
                role="MEMBER",
                is_active=True,
                is_verified=True,
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
                message=f"{member.full_name} ({email}) has registered and can now select a membership plan."
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
        user = CustomUser.objects.filter(email=value).first()
        if user and user.is_active:
            raise serializers.ValidationError(
                "User with this email already exists."
            )
        return value

    def validate_phone(self, value):
        member = Member.objects.filter(phone=value).first()
        if member and not member.is_deleted:
            raise serializers.ValidationError(
                "Member with this phone already exists."
            )
        return value
    
    def create(self, validated_data):
        from accounts.services.membership_service import MembershipService
        from accounts.services.email_service import EmailService

        email = validated_data.pop("email")
        plan = validated_data.pop("plan_id", None)

        DEFAULT_PASSWORD = "Member@123"

        with transaction.atomic():
            user = CustomUser.objects.filter(email=email).first()
            
            if user:
                # Reactivate existing inactive user
                user.is_active = True
                user.is_verified = True
                user.password = make_password(DEFAULT_PASSWORD)
                user.save()
            else:
                user = CustomUser.objects.create(
                    email=email,
                    role="MEMBER",
                    is_active=True,
                    is_verified=True,
                    password=make_password(DEFAULT_PASSWORD),
                )

            member = Member.objects.filter(user=user).first()
            if member:
                # Reactivate existing deleted member
                member.is_deleted = False
                member.created_at = timezone.now() # ✅ Reset join date to today
                for key, value in validated_data.items():
                    setattr(member, key, value)
                member.save()
            else:
                member = Member.objects.create(
                    user=user,
                    email=email,
                    **validated_data
                )

            # ✅ Activate membership if plan selected
            if plan:
                try:
                    MembershipService.activate_membership(
                        member=member,
                        plan=plan,
                        payment_method="cash"
                    )
                except Exception as e:
                    logger.error(f"Failed to activate membership for {member.full_name} during admin creation: {str(e)}")
                    # We don't re-raise here so that the member is still created and welcome email is sent
        
        # ✅ Send welcome email after transaction success
        EmailService.send_welcome_email(
            email=email,
            full_name=member.full_name,
            password=DEFAULT_PASSWORD
        )

        return member


class MemberWorkoutPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutPlan
        fields = ["id", "name", "description", "exercises", "day", "end_time", "status", "start_date", "end_date"]
        
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
    attendance_streak = serializers.SerializerMethodField()
    scheduled_memberships = serializers.SerializerMethodField()


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
            "attendance_streak",
            "assigned_trainer_id",      # ✅ MUST BE HERE
            "assigned_trainer_name",    # ✅ MUST BE HERE
            "join_date",                # ✅ MUST BE HERE
            "height",
            "weight",
            "goal_weight",
            "active_membership",
            "scheduled_memberships",
            "workout_plans",   
            "diet_plans",
            
        ]
    def get_can_change_plan(self, obj):
        active_membership = obj.memberships.filter(status="active").exists()
        return not active_membership

    def get_attendance_streak(self, obj):
        attendance = obj.attendance.order_by("-date")
        if not attendance.exists():
            return 0
        
        streak = 0
        current_date = timezone.now().date()
        
        # Check if they attended today or yesterday to continue streak
        last_attendance = attendance[0].date
        if last_attendance < current_date - timezone.timedelta(days=1):
            return 0
            
        expected_date = last_attendance
        for record in attendance:
            if record.date == expected_date:
                streak += 1
                expected_date -= timezone.timedelta(days=1)
            else:
                break
        return streak
    
    def get_active_membership(self, obj):
        membership = obj.memberships.filter(status="active").first()
        if not membership or not membership.plan:
            return None

        return {
            "plan_id": membership.plan.id,
            "plan_name": membership.plan.name,
            "start_date": membership.start_date,
            "end_date": membership.end_date,
            "status": membership.status
        }

    def get_scheduled_memberships(self, obj):
        memberships = obj.memberships.filter(status="scheduled").order_by("start_date")
        return [
            {
                "plan_id": m.plan.id if m.plan else None,
                "plan_name": m.plan.name if m.plan else "Unknown",
                "start_date": m.start_date,
                "end_date": m.end_date,
                "status": m.status
            } for m in memberships
        ]

        
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

        old_status = instance.status
        new_status = validated_data.get("status", old_status)

        # Handle membership change
        plan_activated = False
        if "plan_id" in validated_data:
            plan = validated_data.get("plan_id")
            if plan:
                MembershipService.activate_membership(
                    member=instance,
                    plan=plan,
                    payment_method="cash"
                )
                plan_activated = True
                new_status = "active"

        # Update normal fields Let status be updated here
        if "status" in validated_data and not plan_activated:
            if new_status != old_status:
                user = instance.user
                from accounts.services.email_service import EmailService
                
                if new_status == "active":
                    user.is_active = True
                    user.is_verified = True
                    user.save()
                    EmailService.send_account_activation_email(user.email, instance.full_name)
                elif new_status == "inactive":
                    user.is_active = False
                    user.save()
                    EmailService.send_account_inactivation_email(user.email, instance.full_name)

        if "status" in validated_data:
            instance.status = new_status

        if "goal" in validated_data:
            instance.goal = validated_data.get("goal")

        instance.save()
        return instance
