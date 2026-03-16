from django.urls import path
from .views import MemberAttendanceAPIView, TrainerAttendanceAPIView, TrainerMemberAttendanceAPIView, AdminAttendanceAPIView

urlpatterns = [
    path('members/', MemberAttendanceAPIView.as_view(), name='member-attendance'),
    path('trainers/', TrainerAttendanceAPIView.as_view(), name='trainer-attendance'),
    path('trainer/members/', TrainerMemberAttendanceAPIView.as_view(), name='trainer-member-attendance'),
    path('admin/overview/', AdminAttendanceAPIView.as_view(), name='admin-attendance-overview'),
]
