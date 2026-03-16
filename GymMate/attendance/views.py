from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from accounts.models import MemberAttendance, TrainerAttendance, Member, Trainer, TrainerBreak
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
            if not attendance.check_in or attendance.check_out:
                if not attendance.check_in:
                    attendance.check_in = now
                attendance.check_out = None
                attendance.status = 'present'
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
            if not attendance.check_in or attendance.check_out:
                if not attendance.check_in:
                    attendance.check_in = now
                attendance.check_out = None
                attendance.status = 'present'
                attendance.save()
                return Response({"message": "Checked in successfully", "time": now.strftime('%H:%M')})
            return Response({"message": "Already checked in"}, status=status.HTTP_400_BAD_REQUEST)
        
        elif action == 'check-out':
            if attendance.check_in and not attendance.check_out:
                # Close any open breaks before checking out
                open_breaks = attendance.breaks.filter(end_time__isnull=True)
                for b in open_breaks:
                    b.end_time = now
                    b.save()
                
                attendance.check_out = now
                attendance.save()
                return Response({"message": "Checked out successfully", "time": now.strftime('%H:%M')})
            elif not attendance.check_in:
                return Response({"message": "Must check in first"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Already checked out"}, status=status.HTTP_400_BAD_REQUEST)

        elif action == 'break-start':
            if attendance.check_in and not attendance.check_out:
                if attendance.breaks.filter(end_time__isnull=True).exists():
                    return Response({"message": "Already on break"}, status=status.HTTP_400_BAD_REQUEST)
                TrainerBreak.objects.create(attendance=attendance, start_time=now)
                return Response({"message": "Break started", "time": now.strftime('%H:%M')})
            return Response({"message": "Must be checked in to take a break"}, status=status.HTTP_400_BAD_REQUEST)

        elif action == 'break-end':
            open_break = attendance.breaks.filter(end_time__isnull=True).first()
            if open_break:
                open_break.end_time = now
                open_break.save()
                return Response({"message": "Break ended", "time": now.strftime('%H:%M')})
            return Response({"message": "No active break found"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

class TrainerMemberAttendanceAPIView(APIView):
    permission_classes = [IsTrainer]

    def get(self, request):
        trainer = get_object_or_404(Trainer, user=request.user)
        date_str = request.query_params.get('date')
        
        # Get all members assigned to this trainer
        assigned_members = Member.objects.filter(assigned_trainer=trainer, is_deleted=False)
        total_assigned = assigned_members.count()

        if date_str:
            try:
                date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                date = timezone.now().date()
            
            # For a specific date, return only that date's records
            attendance_records = MemberAttendance.objects.filter(
                member__in=assigned_members,
                date=date
            ).order_by('-check_in')
        else:
            date = timezone.now().date()
            # For the dashboard (overall view), return all/recent history for trends
            attendance_records = MemberAttendance.objects.filter(
                member__in=assigned_members
            ).order_by('-date')

        # Present today is always based on today's date for stats
        present_count = MemberAttendance.objects.filter(
            member__in=assigned_members,
            date=timezone.now().date(),
            status='present'
        ).count()

        serializer = MemberAttendanceSerializer(attendance_records, many=True)
        
        return Response({
            "date": date,
            "attendance": serializer.data,
            "stats": {
                "total_members": total_assigned,
                "present_today": present_count,
                "absent_today": total_assigned - present_count,
                "attendance_rate": (present_count / total_assigned * 100) if total_assigned > 0 else 0
            }
        })

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
