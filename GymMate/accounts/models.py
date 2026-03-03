import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.conf import settings
from dateutil.relativedelta import relativedelta
from django.db.models import Q


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "ADMIN")

        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("ADMIN", "Admin"),
        ("TRAINER", "Trainer"),
        ("MEMBER", "Member"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    email = models.EmailField(unique=True)
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="MEMBER")
    
    is_active = models.BooleanField(default=True)
    
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    
    username = models.CharField(max_length=150)
    
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"
    class Meta:
        db_table = "GymMate_Users"



class MembershipPlan(models.Model):
    PLAN_CHOICES = [
        ("basic", "Basic"),
        ("premium", "Premium"),
        ("vip", "VIP"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    duration_months = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "GymMate_membership_plans"

    def __str__(self):
        return self.name

class Trainer(TimeStampedModel):
    SPECIALIZATION_CHOICES = [
        ("strength", "Strength"),
        ("cardio", "Cardio"),
        ("yoga", "Yoga"),
        ("crossfit", "Crossfit"),
        ("nutrition", "Nutrition"),
        ("general", "General"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="trainer_profile"
    )
    
    full_name = models.CharField(max_length=255)
    
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    avatar_url = models.URLField(blank=True, null=True)

    specialization = models.CharField(
        max_length=20,
        choices=SPECIALIZATION_CHOICES,
        default="general"
    )

    experience_years = models.PositiveIntegerField(default=0)
    
    certifications = models.JSONField(default=list, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    bio = models.TextField(blank=True, null=True)
    
    
    
    date_joined = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "GymMate_trainers"
        
    def __str__(self):
        return self.full_name
    
# class Member(TimeStampedModel):

#     STATUS_CHOICES = [
#         ("active", "Active"),
#         ("inactive", "Inactive"),
#         ("expired", "Expired"),
#     ]

#     GOAL_CHOICES = [
#         ("weight_loss", "Weight Loss"),
#         ("muscle_gain", "Muscle Gain"),
#         ("maintenance", "Maintenance"),
#         ("endurance", "Endurance"),
#     ]

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

#     user = models.OneToOneField(
#         CustomUser,
#         on_delete=models.CASCADE,
#         related_name="member_profile"
#     )
  
#     email = models.EmailField(unique=True)
   
#     phone = models.CharField(max_length=15, blank=True, null=True,unique=True)
    
#     full_name = models.CharField(max_length=255)
#     avatar_url = models.URLField(blank=True, null=True)

#     assigned_trainer = models.ForeignKey(
#         Trainer,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="members"
#     )

#     membership_plan = models.ForeignKey(
#         MembershipPlan,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="members"
#     )

#     membership_start = models.DateField(null=True, blank=True)
#     membership_end = models.DateField(null=True, blank=True)

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default="active"
#     )

#     height = models.FloatField(null=True, blank=True)
#     weight = models.FloatField(null=True, blank=True)

#     goal = models.CharField(
#         max_length=20,
#         choices=GOAL_CHOICES,
#         default="maintenance"
#     )
    
#     class Meta:
#         db_table = "GymMate_members"
        
#     def __str__(self):
#         return self.full_name

class Member(TimeStampedModel):

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("expired", "Expired"),
    ]

    GOAL_CHOICES = [
        ("weight_loss", "Weight Loss"),
        ("muscle_gain", "Muscle Gain"),
        ("maintenance", "Maintenance"),
        ("endurance", "Endurance"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="member_profile"
    )
  
    email = models.EmailField(unique=True)
   
    phone = models.CharField(max_length=15, blank=True, null=True,unique=True)
    
    full_name = models.CharField(max_length=255)
    avatar_url = models.URLField(blank=True, null=True)

    assigned_trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)

    goal = models.CharField(
        max_length=20,
        choices=GOAL_CHOICES,
        default="maintenance"
    )
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = "GymMate_members"
        
    def __str__(self):
        return self.full_name

class MemberMembership(TimeStampedModel):

    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    plan = models.ForeignKey(
        MembershipPlan,
        on_delete=models.SET_NULL,
        null=True,
        related_name="memberships"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    auto_renew = models.BooleanField(default=False)

    class Meta:
        
        constraints = [
        models.UniqueConstraint(
            fields=["member"],
            condition=Q(status="active"),
            name="unique_active_membership_per_member"
        )
    ]
        indexes = [
        models.Index(fields=["end_date"]),
        models.Index(fields=["status"]),
    ]
        
        db_table = "GymMate_member_memberships"

    def __str__(self):
        return f"{self.member.full_name} - {self.plan.name}"

    def save(self, *args, **kwargs):
        if self.start_date and self.plan and not self.end_date:
            self.end_date = self.start_date + relativedelta(
                months=self.plan.duration_months
            )
        super().save(*args, **kwargs)
        
        if self.status == "active":
            MemberMembership.objects.filter(
                member=self.member,
                status="active"
            ).exclude(id=self.id).update(status="expired")

        

class MembersAttendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="attendance"
    )

    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="present"
    )

    class Meta:
        unique_together = ("member", "date")
        db_table = "GymMate_members_attendance"

    def __str__(self):
        return f"{self.member.full_name} - {self.date}"


class WorkoutPlan(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("paused", "Paused"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="workout_plans"
    )
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        related_name="workout_plans"
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    exercises = models.JSONField(default=list)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )
    class Meta:
        db_table = "GymMate_workoutplans"
    def __str__(self):
        return self.name


class DietPlan(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("paused", "Paused"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="diet_plans"
    )
    
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        related_name="diet_plans"
    )

    name = models.CharField(max_length=255)

    daily_calories = models.PositiveIntegerField()
    protein_grams = models.PositiveIntegerField()
    carbs_grams = models.PositiveIntegerField()
    fat_grams = models.PositiveIntegerField()

    meals = models.JSONField(default=list)
    notes = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )
    
    class Meta:
        db_table = "GymMate_dietplans"
    def __str__(self):
        return self.name


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("upi", "UPI"),
        ("bank_transfer", "Bank Transfer"),
    ]

    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("pending", "Pending"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    membership = models.ForeignKey(
    MemberMembership,
    on_delete=models.SET_NULL,
    null=True,
    related_name="payments"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="cash"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    gateway_response = models.JSONField(blank=True, null=True)

    invoice_number = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "GymMate_payment"
    def __str__(self):
        return self.invoice_number
    

class Notification(TimeStampedModel):

    TYPE_CHOICES = [
        ("admin", "Admin"),
        ("member", "Member"),
        ("trainer", "Trainer"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    title = models.CharField(max_length=255)
    message = models.TextField()

    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = "GymMate_notifications"

    def __str__(self):
        return self.title


