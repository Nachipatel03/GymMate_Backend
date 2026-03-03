from rest_framework import serializers
from django.utils import timezone
from accounts.models import Payment, Member, MembershipPlan, MemberMembership
from dateutil.relativedelta import relativedelta
import uuid


class PaymentCreateSerializer(serializers.ModelSerializer):
    member = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all()
    )

    plan = serializers.PrimaryKeyRelatedField(
        queryset=MembershipPlan.objects.all()
    )

    class Meta:
        model = Payment
        fields = [
            "member",
            "plan",
            "amount",
            "payment_method",
        ]

    def create(self, validated_data):
        member = validated_data.pop("member")
        plan = validated_data.pop("plan")

        today = timezone.now().date()

        # ✅ Create Membership
        membership = MemberMembership.objects.create(
            member=member,
            plan=plan,
            start_date=today,
            end_date=today + relativedelta(months=plan.duration_months),
            status="active",
        )

        # ✅ Create Payment linked to membership
        payment = Payment.objects.create(
            member=member,
            membership=membership,
            amount=validated_data["amount"],
            payment_date=today,
            payment_method=validated_data["payment_method"],
            status="completed",
            invoice_number=f"INV-{uuid.uuid4().hex[:8]}",
        )

        return payment
