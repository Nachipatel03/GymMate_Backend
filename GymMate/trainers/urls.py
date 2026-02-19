from django.urls import path
from .views import TrainerListCreateAPIView,AdminTrainerDetailAPIView,WorkoutPlanAPIView,WorkoutPlanDetailAPIView

urlpatterns = [
    path("byadmintrainers/", TrainerListCreateAPIView.as_view(), name="trainer-list-create"),
    path("trainers/<uuid:trainer_id>/",AdminTrainerDetailAPIView.as_view()),
    path("workout-plans/", WorkoutPlanAPIView.as_view(), name="workout-plans"),
    path("workout-plans/<uuid:pk>/", WorkoutPlanDetailAPIView.as_view()),
]