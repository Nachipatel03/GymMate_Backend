from django.urls import path
from .views import MembershipPlanCreateAPIView

urlpatterns = [
    path("membership-plans/", MembershipPlanCreateAPIView.as_view()),
]