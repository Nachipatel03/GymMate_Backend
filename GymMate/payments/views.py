from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from dateutil.relativedelta import relativedelta
from .serializers import PaymentCreateSerializer, PaymentListSerializer, MemberPaymentCreateSerializer
from accounts.models import Payment

# Create your views here.
class CreatePaymentAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()

        return Response({
            "message": f"Payment successful & Membership {payment.membership.status} until {payment.membership.end_date}"
        }, status=201)

class MemberCheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != "MEMBER":
            return Response({"detail": "Only members can checkout."}, status=403)

        serializer = MemberPaymentCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()

        return Response({
            "message": f"Payment successful & Membership {payment.membership.status} until {payment.membership.end_date}",
            "invoice_number": payment.invoice_number
        }, status=201)

from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

class PaymentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class PaymentListAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        search_query = request.query_params.get("search", "")
        status_filter = request.query_params.get("status", "all")
        
        payments = Payment.objects.all()

        if status_filter != "all":
            payments = payments.filter(status=status_filter)

        if search_query:
            payments = payments.filter(
                Q(invoice_number__icontains=search_query) |
                Q(member__full_name__icontains=search_query) |
                Q(member__email__icontains=search_query)
            )

        payments = payments.order_by("-created_at")
        
        paginator = PaymentPagination()
        paginated_payments = paginator.paginate_queryset(payments, request)
        serializer = PaymentListSerializer(paginated_payments, many=True)
        return paginator.get_paginated_response(serializer.data)

class RevenueStatsAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.now().date()
        first_day_of_month = today.replace(day=1)
        
        total_revenue = Payment.objects.filter(status="completed").aggregate(Sum("amount"))["amount__sum"] or 0
        this_month_revenue = Payment.objects.filter(
            status="completed", 
            payment_date__gte=first_day_of_month
        ).aggregate(Sum("amount"))["amount__sum"] or 0
        
        pending_amount = Payment.objects.filter(status="pending").aggregate(Sum("amount"))["amount__sum"] or 0
        
        six_months_ago = (today.replace(day=1) - relativedelta(months=5))
        
        monthly_revenue = Payment.objects.filter(
            status="completed",
            payment_date__gte=six_months_ago
        ).annotate(
            month=TruncMonth('payment_date')
        ).values('month').annotate(
            revenue=Sum('amount')
        ).order_by('month')

        # Map results to last 6 months to ensure all months exist
        revenue_map = {r['month']: float(r['revenue']) for r in monthly_revenue}
        trend_data = []
        for i in range(5, -1, -1):
            m_start = today.replace(day=1) - relativedelta(months=i)
            # Normalize to start of month for mapping
            m_key = m_start.replace(day=1)
            trend_data.append({
                "name": m_start.strftime("%b"),
                "revenue": revenue_map.get(m_key, 0.0)
            })

        # Payment methods distribution
        methods_data = []
        methods = ["cash", "card", "upi", "bank_transfer"]
        colors = ["#10b981", "#8b5cf6", "#06b6d4", "#f59e0b"]
        
        for idx, method in enumerate(methods):
            val = Payment.objects.filter(payment_method=method, status="completed").count()
            if val > 0:
                methods_data.append({
                    "name": method.replace("_", " ").capitalize(),
                    "value": val,
                    "color": colors[idx]
                })

        return Response({
            "total_revenue": total_revenue,
            "this_month_revenue": this_month_revenue,
            "pending_amount": pending_amount,
            "total_transactions": Payment.objects.count(),
            "trend": trend_data,
            "methods": methods_data
        })