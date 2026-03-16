from django.urls import path
from .views import MembershipPlanCreateAPIView,MembershipPlanDetailAPIView, AvailableMembershipPlansAPIView

urlpatterns = [
    path("membership-plans/", MembershipPlanCreateAPIView.as_view()),
    path("membership-plans/<uuid:pk>/", MembershipPlanDetailAPIView.as_view()),
    path("available/", AvailableMembershipPlansAPIView.as_view()),
]