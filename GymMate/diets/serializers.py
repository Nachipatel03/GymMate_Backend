from rest_framework import serializers
from .models import DietPlan, DailyProgress
from accounts.models import Member

class DailyProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyProgress
        fields = ['id', 'member', 'date', 'water_consumed', 'completed_meals']
        read_only_fields = ['id', 'member', 'date']

class DietPlanSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    trainer_name = serializers.CharField(source='trainer.full_name', read_only=True)
    member_id = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(),
        source='member',
        write_only=True
    )

    class Meta:
        model = DietPlan
        fields = [
            'id', 'name', 'member', 'member_id', 'member_name', 
            'trainer', 'trainer_name', 'daily_calories', 
            'protein_grams', 'carbs_grams', 'fat_grams', 'meals',
            'notes', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'trainer', 'created_at', 'updated_at', 'member']

    def validate(self, data):
        # Additional validation if needed
        return data
