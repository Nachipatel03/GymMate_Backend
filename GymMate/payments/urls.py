from django.urls import path
from .views import CreatePaymentAPIView

urlpatterns = [
    path(
        "payments/create/",
        CreatePaymentAPIView.as_view(),
        name="create-payment"
    ),
]
