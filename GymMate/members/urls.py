from django.urls import path
from .views import (
    AdminMemberListCreateAPIView, 
    AdminMemberDetailAPIView,
    MemberWorkoutPlanListAPIView,
    MemberProfileAPIView,
    MemberProgressAPIView
)

urlpatterns = [
   path("members/", AdminMemberListCreateAPIView.as_view()),
   path("members/<uuid:member_id>/", AdminMemberDetailAPIView.as_view()),
   path("my-workout-plans/", MemberWorkoutPlanListAPIView.as_view(), name="member-workout-plans"),
   path("profile/", MemberProfileAPIView.as_view(), name="member-profile-detail"),
   path("my-progress/", MemberProgressAPIView.as_view(), name="member-progress"),
]