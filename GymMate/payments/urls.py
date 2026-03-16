from django.urls import path
from .views import CreatePaymentAPIView, PaymentListAPIView, RevenueStatsAPIView, MemberCheckoutAPIView

urlpatterns = [
    path(
        "checkout/",
        MemberCheckoutAPIView.as_view(),
        name="member-checkout"
    ),
    path(
        "payments/create/",
        CreatePaymentAPIView.as_view(),
        name="create-payment"
    ),
    path(
        "payments/list/",
        PaymentListAPIView.as_view(),
        name="payment-list"
    ),
    path(
        "revenue/stats/",
        RevenueStatsAPIView.as_view(),
        name="revenue-stats"
    ),
]
