from django.db import models
import uuid
from accounts.models import Member, Trainer

class DietPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='diet_plans')
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='created_diet_plans')
    daily_calories = models.PositiveIntegerField()
    protein_grams = models.PositiveIntegerField()
    carbs_grams = models.PositiveIntegerField()
    fat_grams = models.PositiveIntegerField()
    meals = models.JSONField(default=list)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "GymMate_diet_plans"

    def __str__(self):
        return f"{self.name} for {self.member.full_name}"

class DailyProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='daily_progress')
    date = models.DateField(auto_now_add=True)
    water_consumed = models.FloatField(default=0.0)
    completed_meals = models.JSONField(default=list) # List of meal names or IDs completed today

    class Meta:
        db_table = "GymMate_daily_progress"
        unique_together = ('member', 'date')

    def __str__(self):
        return f"Progress for {self.member.full_name} on {self.date}"
