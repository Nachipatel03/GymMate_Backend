from django.urls import path
from .views import AdminMemberListCreateAPIView

urlpatterns = [
   path("members/", AdminMemberListCreateAPIView.as_view()),
]