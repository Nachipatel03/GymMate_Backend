from django.urls import path
from .views import TrainerListCreateAPIView,AdminTrainerDetailAPIView

urlpatterns = [
    path("byadmintrainers/", TrainerListCreateAPIView.as_view(), name="trainer-list-create"),
    path("trainers/<uuid:trainer_id>/",AdminTrainerDetailAPIView.as_view()),
]