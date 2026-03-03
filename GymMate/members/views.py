from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from accounts.permissions import IsAdminOrTrainer

from django.db.models import Count
from rest_framework import status
from django.shortcuts import get_object_or_404

from accounts.models import Member
from .serializers import MemberAdminCreateSerializer, MemberSerializer,MemberAdminUpdateSerializer


class AdminMemberListCreateAPIView(APIView):
    permission_classes = [IsAdminOrTrainer]

    def get(self, request):

        if request.user.role == "ADMIN":
           members = Member.objects.filter(is_deleted=False)
        elif request.user.role == "TRAINER":
            trainer = request.user.trainer_profile
            members = (
            Member.objects
            .filter(
                assigned_trainer=trainer,
                is_deleted=False
            )
            .select_related("user", "assigned_trainer")
            .prefetch_related("workout_plans", "diet_plans")
        )

        else:
            return Response(
                {"error": "Not authorized"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)

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
    permission_classes = [IsAdminOrTrainer]
    

    def get_object(self, request, member_id):
        if request.user.role == "ADMIN":
            return get_object_or_404(
                Member.objects.select_related("user", "assigned_trainer").filter(is_deleted=False),
                id=member_id
            )
        elif request.user.role == "TRAINER":
            return get_object_or_404(
                Member.objects.select_related("user", "assigned_trainer").filter(is_deleted=False, assigned_trainer=request.user.trainer_profile),
                id=member_id
            )
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to perform this action.")

    # ✅ GET single member
    def get(self, request, member_id):
        member = self.get_object(request, member_id)
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


    def delete(self, request, member_id):
        member = self.get_object(request, member_id)
        user = member.user

        member.is_deleted = True
        member.status = "inactive"
        member.save()
        member.memberships.filter(status="active").update(status="cancelled")
        user.is_active = False
        user.save()

        return Response(
            {"message": "Member and user deleted successfully"},
            status=status.HTTP_200_OK
        )