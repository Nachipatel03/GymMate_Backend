from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Trainer
from .serializers import TrainerSerializer,TrainerAdminCreateSerializer
from rest_framework import permissions
from django.db.models import Count


class TrainerListCreateAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        trainers = Trainer.objects.annotate(
            assigned_members_count=Count("assigned_members")
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