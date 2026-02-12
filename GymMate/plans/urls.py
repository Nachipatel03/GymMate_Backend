from django.urls import path
from .views import MembershipPlanCreateAPIView,MembershipPlanDetailAPIView

urlpatterns = [
    path("membership-plans/", MembershipPlanCreateAPIView.as_view()),
    path("membership-plans/<uuid:pk>/", MembershipPlanDetailAPIView.as_view()),
]