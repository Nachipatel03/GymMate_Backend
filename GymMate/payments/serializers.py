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
            "status",
            "due_date",
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
            status=validated_data.get("status", "completed"),
            due_date=validated_data.get("due_date"),
            invoice_number=f"INV-{uuid.uuid4().hex[:8]}",
        )

        return payment


class PaymentListSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.full_name", read_only=True)
    member_email = serializers.EmailField(source="member.email", read_only=True)
    plan_name = serializers.CharField(source="membership.plan.name", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "member_name",
            "member_email",
            "amount",
            "payment_method",
            "status",
            "payment_date",
            "due_date",
            "plan_name",
            "invoice_number",
        ]
