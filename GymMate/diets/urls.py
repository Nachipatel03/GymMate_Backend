from django.urls import path
from .views import TrainerDietPlanListCreateView, TrainerDietPlanDetailView, MemberDietPlanListView, DailyProgressView

urlpatterns = [
    path("trainer-plans/", TrainerDietPlanListCreateView.as_view(), name="trainer-diet-plans"),
    path("trainer-plans/<uuid:pk>/", TrainerDietPlanDetailView.as_view(), name="trainer-diet-plan-detail"),
    path("my-plans/", MemberDietPlanListView.as_view(), name="member-diet-plans"),
    path("daily-progress/", DailyProgressView.as_view(), name="daily-progress"),
]
