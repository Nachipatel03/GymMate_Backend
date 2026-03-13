from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import PaymentCreateSerializer, PaymentListSerializer, MemberPaymentCreateSerializer
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
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

class PaymentListAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        payments = Payment.objects.all().order_by("-created_at")
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)

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
        
        # Monthly trend for the last 6 months
        trend_data = []
        for i in range(5, -1, -1):
            from dateutil.relativedelta import relativedelta
            m_start = today.replace(day=1) - relativedelta(months=i)
            m_end = m_start + relativedelta(months=1) - timedelta(days=1)
            
            m_revenue = Payment.objects.filter(
                status="completed",
                payment_date__range=[m_start, m_end]
            ).aggregate(Sum("amount"))["amount__sum"] or 0
            
            trend_data.append({
                "name": m_start.strftime("%b"),
                "revenue": float(m_revenue)
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