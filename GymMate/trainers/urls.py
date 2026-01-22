from django.urls import path
from .views import TrainerListCreateAPIView

urlpatterns = [
    path("byadmintrainers/", TrainerListCreateAPIView.as_view(), name="trainer-list-create"),
]