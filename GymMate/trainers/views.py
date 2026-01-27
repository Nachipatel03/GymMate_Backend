from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Trainer
from .serializers import TrainerSerializer,TrainerAdminCreateSerializer
from rest_framework import permissions
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
