from django.urls import path
from .views import AdminMemberListCreateAPIView,AdminMemberDetailAPIView

urlpatterns = [
   path("members/", AdminMemberListCreateAPIView.as_view()),
   path("members/<uuid:member_id>/", AdminMemberDetailAPIView.as_view()),
]