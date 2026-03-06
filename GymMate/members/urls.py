from django.urls import path
from .views import (
    AdminMemberListCreateAPIView, 
    AdminMemberDetailAPIView,
    MemberWorkoutPlanListAPIView,
    MemberProfileAPIView,
    MemberProgressAPIView,
    TrainerMemberProgressAPIView
)

urlpatterns = [
   path("members/", AdminMemberListCreateAPIView.as_view()),
   path("members/<uuid:member_id>/", AdminMemberDetailAPIView.as_view()),
   path("members/<uuid:member_id>/progress/", TrainerMemberProgressAPIView.as_view(), name="trainer-member-progress"),
   path("my-workout-plans/", MemberWorkoutPlanListAPIView.as_view(), name="member-workout-plans"),
   path("profile/", MemberProfileAPIView.as_view(), name="member-profile-detail"),
   path("my-progress/", MemberProgressAPIView.as_view(), name="member-progress"),
]