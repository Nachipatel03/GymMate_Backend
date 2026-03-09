from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from accounts.models import MemberAttendance, TrainerAttendance, Member, Trainer
from .serializers import MemberAttendanceSerializer, TrainerAttendanceSerializer
from django.shortcuts import get_object_or_404
from accounts.permissions import IsTrainer

class MemberAttendanceAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        member = get_object_or_404(Member, user=request.user)
        attendance = MemberAttendance.objects.filter(member=member).order_by('-date')
        serializer = MemberAttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

    def post(self, request):
        member = get_object_or_404(Member, user=request.user)
        action = request.data.get('action') # 'check-in' or 'check-out'
        today = timezone.now().date()
        now = timezone.now().time()

        attendance, created = MemberAttendance.objects.get_or_create(
            member=member, 
            date=today,
            defaults={'status': 'present'}
        )

        if action == 'check-in':
            if not attendance.check_in:
                attendance.check_in = now
                attendance.save()
                return Response({"message": "Checked in successfully", "time": now.strftime('%H:%M')})
            return Response({"message": "Already checked in"}, status=status.HTTP_400_BAD_REQUEST)
        
        elif action == 'check-out':
            if attendance.check_in and not attendance.check_out:
                attendance.check_out = now
                attendance.save()
                return Response({"message": "Checked out successfully", "time": now.strftime('%H:%M')})
            elif not attendance.check_in:
                return Response({"message": "Must check in first"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Already checked out"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

class TrainerAttendanceAPIView(APIView):
    permission_classes = [IsTrainer]

    def get(self, request):
        trainer = get_object_or_404(Trainer, user=request.user)
        attendance = TrainerAttendance.objects.filter(trainer=trainer).order_by('-date')
        serializer = TrainerAttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

    def post(self, request):
        trainer = get_object_or_404(Trainer, user=request.user)
        action = request.data.get('action')
        today = timezone.now().date()
        now = timezone.now().time()

        attendance, created = TrainerAttendance.objects.get_or_create(
            trainer=trainer, 
            date=today,
            defaults={'status': 'present'}
        )

        if action == 'check-in':
            if not attendance.check_in:
                attendance.check_in = now
                attendance.save()
                return Response({"message": "Checked in successfully", "time": now.strftime('%H:%M')})
            return Response({"message": "Already checked in"}, status=status.HTTP_400_BAD_REQUEST)
        
        elif action == 'check-out':
            if attendance.check_in and not attendance.check_out:
                attendance.check_out = now
                attendance.save()
                return Response({"message": "Checked out successfully", "time": now.strftime('%H:%M')})
            elif not attendance.check_in:
                return Response({"message": "Must check in first"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Already checked out"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

class TrainerMemberAttendanceAPIView(APIView):
    permission_classes = [IsTrainer]

    def get(self, request):
        trainer = get_object_or_404(Trainer, user=request.user)
        # Get attendance for all members assigned to this trainer who are not deleted
        attendance = MemberAttendance.objects.filter(
            member__assigned_trainer=trainer,
            member__is_deleted=False
        ).order_by('-date')
        serializer = MemberAttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

class AdminAttendanceAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        date_str = request.query_params.get('date')
        if date_str:
            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = timezone.now().date()

        member_attendance = MemberAttendance.objects.filter(date=date, member__is_deleted=False)
        trainer_attendance = TrainerAttendance.objects.filter(date=date)

        member_serializer = MemberAttendanceSerializer(member_attendance, many=True)
        trainer_serializer = TrainerAttendanceSerializer(trainer_attendance, many=True)

        # Stats
        total_members = Member.objects.filter(is_deleted=False).count()
        present_members = member_attendance.filter(status='present').count()
        total_trainers = Trainer.objects.filter(status='active').count()
        present_trainers = trainer_attendance.filter(status='present').count()

        return Response({
            "date": date,
            "member_attendance": member_serializer.data,
            "trainer_attendance": trainer_serializer.data,
            "stats": {
                "total_members": total_members,
                "present_members": present_members,
                "absent_members": total_members - present_members,
                "total_trainers": total_trainers,
                "present_trainers": present_trainers,
                "absent_trainers": total_trainers - present_trainers,
            }
        })
