from rest_framework import serializers
from accounts.models import MembershipPlan


class MembershipPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipPlan
        fields = [
            "id",
            "name",
            "type",
            "duration_months",
            "price",
            "features",
            "is_active",
        ]