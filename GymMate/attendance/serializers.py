from rest_framework import serializers
from accounts.models import MemberAttendance, TrainerAttendance

class MemberAttendanceSerializer(serializers.ModelSerializer):
    member_name = serializers.ReadOnlyField(source='member.full_name')

    class Meta:
        model = MemberAttendance
        fields = [
            'id', 'member', 'member_name', 'date', 
            'check_in', 'check_out', 'status'
        ]

class TrainerAttendanceSerializer(serializers.ModelSerializer):
    trainer_name = serializers.ReadOnlyField(source='trainer.full_name')

    class Meta:
        model = TrainerAttendance
        fields = [
            'id', 'trainer', 'trainer_name', 'date', 
            'check_in', 'check_out', 'status'
        ]
