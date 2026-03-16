from rest_framework import serializers
from accounts.models import Trainer,CustomUser,Member,WorkoutPlan
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.shortcuts import get_object_or_404


class TrainerAdminCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    assigned_members_count = serializers.IntegerField(read_only=True)
    trainer_email = serializers.EmailField(
        source="user.email",
        read_only=True
    )
    class Meta:
        model = Trainer
        fields = [
             "id",    
            "trainer_email",  
            "email",
            "full_name",
            "phone",
            "avatar_url",
            "specialization",
            "experience_years",
            "certifications",
             "assigned_members_count",
            "status",
            "bio",
        ]
        read_only_fields = [
             "id",    
            "assigned_members_count",
        ]
    def create(self, validated_data):
        email = validated_data.pop("email")
        DEFAULT_PASSWORD = "@Nick0314"

        try:
            with transaction.atomic():
                # 1️⃣ Create user
                user = CustomUser.objects.create(
                    email=email,
                    role="TRAINER",
                    is_active=True,
                    is_staff=True,
                    password=make_password(DEFAULT_PASSWORD),
                )

                # 2️⃣ Create trainer profile
                trainer = Trainer.objects.create(
                    user=user,
                    **validated_data
                )

        except IntegrityError:
            raise serializers.ValidationError({
                "email": "Email already exists"
            })

        return trainer
        
        
    def validate_phone(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Phone must contain only digits")
        return value
    
    def validate_experience_years(self, value):
        if value > 60:
            raise serializers.ValidationError("Experience seems invalid")
        return value

class TrainerSerializer(serializers.ModelSerializer):
    assigned_members_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Trainer
        fields = [
            "id",
            "full_name",
            "phone",
            "email",
            "avatar_url",
            "specialization",
            "experience_years",
            "certifications",
            "status",
            "bio",
            "is_staff",
            "date_joined",
            "assigned_members_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_staff",
            "date_joined",
            "created_at",
            "updated_at",
            "assigned_members_count",
        ]


class WorkoutPlanSerializer(serializers.ModelSerializer):

    member_id = serializers.UUIDField(write_only=True)
    member_id_display = serializers.UUIDField(
        source="member.id",
        read_only=True
    )
    member_name = serializers.CharField(
        source="member.full_name",
        read_only=True
    )

    class Meta:
        model = WorkoutPlan
        fields = [
            "id",
            "name",
            "description",
            "day",
            "end_time",
            "status",
            "exercises",
            "start_date",
            "end_date",
            "member_id",
            "member_id_display",
            "member_name",
        ]
        read_only_fields = ["id", "member_name", "member_id_display"]

    def validate(self, data):
        member_id = data.get("member_id")
        day = data.get("day")
        
        # If member_id is not provided (partial update), we get it from instance
        if not member_id and self.instance:
            member_id = self.instance.member_id
            
        if not day and self.instance:
            day = self.instance.day

        if member_id and day:
            query = WorkoutPlan.objects.filter(member_id=member_id, day=day)
            if self.instance:
                query = query.exclude(id=self.instance.id)
                
            if query.exists():
                raise serializers.ValidationError(
                    f"A workout plan already exists for this member on {day}."
                )
        return data

    def validate_exercises(self, value):
        """
        Ensure exercises list structure is correct
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("Exercises must be a list")

        for exercise in value:
            if "name" not in exercise:
                raise serializers.ValidationError("Each exercise must have a name")
            if "sets" not in exercise:
                raise serializers.ValidationError("Each exercise must have sets")
            if "reps" not in exercise:
                raise serializers.ValidationError("Each exercise must have reps")
            if "day" not in exercise:
                raise serializers.ValidationError("Each exercise must have day")

        return value

    def create(self, validated_data):

        request = self.context.get("request")
        trainer = request.user.trainer_profile

        member_id = validated_data.pop("member_id")

        # 🔒 Only allow members assigned to this trainer
        member = get_object_or_404(
            Member,
            id=member_id,
            assigned_trainer=trainer
        )

        workout = WorkoutPlan.objects.create(
            member=member,
            trainer=trainer,
            **validated_data
        )

        return workout
    
    def update(self, instance, validated_data):
        request = self.context.get("request")
        trainer = request.user.trainer_profile

        member_id = validated_data.pop("member_id", None)

        if member_id:
            member = get_object_or_404(
                Member,
                id=member_id,
                assigned_trainer=trainer
            )
            instance.member = member

        # Update remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance