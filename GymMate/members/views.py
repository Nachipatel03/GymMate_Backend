from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from accounts.permissions import IsAdminOrTrainer, IsMember

from django.db.models import Count
from rest_framework import status
from django.shortcuts import get_object_or_404

from accounts.models import Member, Payment, WorkoutPlan, MemberProgress
from .serializers import (
    MemberAdminCreateSerializer, 
    MemberSerializer, 
    MemberAdminUpdateSerializer,
    MemberWorkoutPlanSerializer,
    MemberProgressSerializer
)


class MemberWorkoutPlanListAPIView(APIView):
    permission_classes = [IsMember]

    def get(self, request):
        member = request.user.member_profile
        workout_plans = WorkoutPlan.objects.filter(member=member)
        serializer = MemberWorkoutPlanSerializer(workout_plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        member = request.user.member_profile
        plan_id = request.data.get("plan_id")
        exercise_idx = request.data.get("exercise_index")
        
        if plan_id is None or exercise_idx is None:
            return Response({"error": "plan_id and exercise_index are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        plan = get_object_or_404(WorkoutPlan, id=plan_id, member=member)
        exercises = plan.exercises
        
        try:
            exercise_idx = int(exercise_idx)
            if 0 <= exercise_idx < len(exercises):
                exercises[exercise_idx]["completed"] = not exercises[exercise_idx].get("completed", False)
                plan.exercises = exercises
                plan.save()
                return Response({
                    "message": "Exercise status updated", 
                    "completed": exercises[exercise_idx]["completed"],
                    "workout_progress": (len([e for e in exercises if e.get("completed")]) / len(exercises)) * 100
                }, status=status.HTTP_200_OK)
        except (ValueError, TypeError):
            pass
        
        return Response({"error": "Invalid exercise index"}, status=status.HTTP_400_BAD_REQUEST)


class MemberProfileAPIView(APIView):
    permission_classes = [IsMember]

    def get(self, request):
        member = request.user.member_profile
        serializer = MemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        member = request.user.member_profile
        serializer = MemberSerializer(member, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class MemberProgressAPIView(APIView):
    permission_classes = [IsMember]

    def get(self, request):
        member = request.user.member_profile
        progress = MemberProgress.objects.filter(member=member).order_by("date", "created_at")
        serializer = MemberProgressSerializer(progress, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        member = request.user.member_profile
        serializer = MemberProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(member=member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TrainerMemberProgressAPIView(APIView):
    """Allows a trainer to view progress logs for any of their assigned members."""
    permission_classes = [IsAdminOrTrainer]

    def get(self, request, member_id):
        trainer = request.user.trainer_profile
        member = get_object_or_404(
            Member,
            id=member_id,
            assigned_trainer=trainer,
            is_deleted=False
        )
        progress = MemberProgress.objects.filter(member=member).order_by("date", "created_at")
        serializer = MemberProgressSerializer(progress, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class AdminMemberListCreateAPIView(APIView):
    permission_classes = [IsAdminOrTrainer]

    def get(self, request):

        if request.user.role == "ADMIN":
           members = Member.objects.filter(is_deleted=False).order_by("-created_at")
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
            .order_by("-created_at")
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
        
        # 💳 Block deletion if there are pending payments
        has_pending = Payment.objects.filter(member=member, status="pending").exists()
        if has_pending:
            return Response(
                {"error": "Cannot delete member. There are pending payments that must be settled first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = member.user

        member.is_deleted = True
        member.status = "inactive"
        member.save()
        member.memberships.filter(status="active").update(status="cancelled")
        user.is_active = False
        user.save()

        from accounts.services.email_service import EmailService
        EmailService.send_account_inactivation_email(user.email, member.full_name)

        return Response(
            {"message": "Member and user deleted successfully"},
            status=status.HTTP_200_OK
        )