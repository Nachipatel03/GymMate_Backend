from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.db.models import Count
from rest_framework import status
from django.shortcuts import get_object_or_404

from accounts.models import Member
from .serializers import MemberAdminCreateSerializer, MemberSerializer,MemberAdminUpdateSerializer


class AdminMemberListCreateAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        members = (
            Member.objects
            .select_related("user",  "assigned_trainer", "membership_plan")
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


class AdminMemberDetailAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, member_id):
        return get_object_or_404(
            Member.objects.select_related("user", "trainer", "membership_plan"),
            id=member_id
        )

    # ✅ GET single member
    def get(self, request, member_id):
        member = self.get_object(member_id)
        serializer = MemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, member_id):
        member = get_object_or_404(Member, id=member_id)

        serializer = MemberAdminUpdateSerializer(
            member,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Member updated successfully"},
            status=status.HTTP_200_OK
        )

    # ❌ DELETE member
    def delete(self, request, member_id):
        member = self.get_object(member_id)

        # Optional: also deactivate user
        member.user.is_active = False
        member.user.save()

        member.delete()

        return Response(
            {"message": "Member deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
