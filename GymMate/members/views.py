from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.db.models import Count

from accounts.models import Member
from .serializers import MemberAdminCreateSerializer, MemberSerializer


class AdminMemberListCreateAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        members = (
            Member.objects
            .select_related("user", "trainer", "membership_plan")
        )

        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MemberAdminCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        member = serializer.save()

        return Response(
            {
                "message": "Member added successfully",
                "member_id": member.id,
                "email": member.user.email,
                "is_verified": member.user.is_verified,
            },
            status=status.HTTP_201_CREATED
        )