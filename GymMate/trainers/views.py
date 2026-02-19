from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Trainer,Member,WorkoutPlan
from .serializers import TrainerSerializer,TrainerAdminCreateSerializer,WorkoutPlanSerializer
from rest_framework import permissions
from accounts.permissions import IsTrainer
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

class TrainerListCreateAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        trainers = Trainer.objects.annotate(
            assigned_members_count=Count("members")
        )

        serializer = TrainerAdminCreateSerializer(trainers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TrainerAdminCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        trainer = serializer.save()

        return Response(
            {
                "message": "Trainer created successfully",
                "trainer_id": trainer.id,
                "email": trainer.user.email,
            },
            status=status.HTTP_201_CREATED
        )

class AdminTrainerDetailAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get_object(self, trainer_id):
        return get_object_or_404(
            Trainer.objects.select_related("user"),
            id=trainer_id
        )
    def get(self, request, trainer_id):
        trainer = self.get_object(trainer_id)
        serializer =TrainerSerializer(trainer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def patch(self, request, trainer_id):
        trainer = self.get_object(trainer_id)

        serializer = TrainerAdminCreateSerializer(
            trainer,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Trainer updated successfully"},
            status=status.HTTP_200_OK
        )

    # 🔹 DELETE
    def delete(self, request, trainer_id):
        trainer = self.get_object(trainer_id)
        if trainer.members.exists():
            raise ValidationError(
                "Trainer cannot be deleted because members are assigned to them."
            )
        # ✅ Delete linked user as well (recommended)
        user = trainer.user
        trainer.delete()
        user.delete()

        return Response(
            {"message": "Trainer deleted successfully"},
            status=status.HTTP_200_OK
        )


class WorkoutPlanAPIView(APIView):
    permission_classes = [IsTrainer]

    def get(self, request):
        trainer = request.user.trainer_profile

        member_id = request.query_params.get("member_id")

        queryset = WorkoutPlan.objects.filter(trainer=trainer)

        if member_id:
            queryset = queryset.filter(member_id=member_id)

        serializer = WorkoutPlanSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = WorkoutPlanSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=201)
    
class WorkoutPlanDetailAPIView(APIView):
    permission_classes = [IsTrainer]

    def get_object(self, request, pk):
        trainer = request.user.trainer_profile

        # 🔒 Only allow trainer to access their own plans
        return get_object_or_404(
            WorkoutPlan,
            id=pk,
            trainer=trainer
        )

    def put(self, request, pk):
        workout = self.get_object(request, pk)

        serializer = WorkoutPlanSerializer(
            workout,
            data=request.data,
            partial=False,  # full update
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        workout = self.get_object(request, pk)

        serializer = WorkoutPlanSerializer(
            workout,
            data=request.data,
            partial=True,  # partial update
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        workout = self.get_object(request, pk)

        workout.delete()

        return Response(
            {"message": "Workout plan deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )