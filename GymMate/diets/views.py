from rest_framework import generics, permissions, status
from accounts.permissions import IsMember
from rest_framework.response import Response
from .models import DietPlan
from .serializers import DietPlanSerializer
from accounts.models import Trainer, Member

class IsAdminOrTrainer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'TRAINER']

class TrainerDietPlanListCreateView(generics.ListCreateAPIView):
    serializer_class = DietPlanSerializer
    permission_classes = [IsAdminOrTrainer]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return DietPlan.objects.all()
        
        # If trainer, only show plans they created
        try:
            trainer = user.trainer_profile
            return DietPlan.objects.filter(trainer=trainer)
        except Trainer.DoesNotExist:
            return DietPlan.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'TRAINER':
            serializer.save(trainer=user.trainer_profile)
        else:
            # For admin, we might want to manually specify trainer or just pick one
            # For now, let's assume admins can't create diets easily without a trainer profile
            # or we pick the first trainer if needed, but usually trainers create these.
            trainer = Trainer.objects.first() # Fallback for testing
            serializer.save(trainer=trainer)

class TrainerDietPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DietPlanSerializer
    permission_classes = [IsAdminOrTrainer]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return DietPlan.objects.all()
        
        try:
            return DietPlan.objects.filter(trainer=user.trainer_profile)
        except Trainer.DoesNotExist:
            return DietPlan.objects.none()

class MemberDietPlanListView(generics.ListAPIView):
    serializer_class = DietPlanSerializer
    permission_classes = [IsMember]

    def get_queryset(self):
        user = self.request.user
        try:
            member = user.member_profile
            return DietPlan.objects.filter(member=member, status="active")
        except Member.DoesNotExist:
            return DietPlan.objects.none()

from .models import DailyProgress
from .serializers import DailyProgressSerializer
from django.utils import timezone

class DailyProgressView(generics.RetrieveUpdateAPIView):
    serializer_class = DailyProgressSerializer
    permission_classes = [IsMember]

    def get_object(self):
        member = self.request.user.member_profile
        today = timezone.now().date()
        progress, created = DailyProgress.objects.get_or_create(member=member, date=today)
        return progress

    def perform_update(self, serializer):
        serializer.save(member=self.request.user.member_profile)
