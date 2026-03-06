import os
import django
import datetime
import random
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GymMate.settings')
django.setup()

from accounts.models import Member, MemberProgress

def seed_data(email):
    try:
        member = Member.objects.get(user__email=email)
        print(f"Seeding data for {member.full_name} ({email})")
        
        # Clear existing progress to avoid duplicates/confusion if preferred
        # MemberProgress.objects.filter(member=member).delete()
        
        start_date = timezone.now().date() - datetime.timedelta(days=365)
        start_weight = 95.0
        target_weight = 71.0
        
        # 12 monthly logs
        for i in range(13):
            log_date = start_date + datetime.timedelta(days=i*30)
            if log_date > timezone.now().date():
                break
                
            # Linear loss with some randomness
            progress_ratio = i / 12
            weight = start_weight - (start_weight - target_weight) * progress_ratio
            weight += random.uniform(-0.5, 0.5)
            
            MemberProgress.objects.update_or_create(
                member=member,
                date=log_date,
                defaults={
                    'weight': round(weight, 1),
                    'notes': f"Monthly check-in {i}",
                    'measurements': {
                        'waist': round(38 - (progress_ratio * 4), 1),
                        'chest': round(42 - (progress_ratio * 2), 1)
                    }
                }
            )
            print(f"Created log for {log_date}: {round(weight, 1)}kg")
            
        # Update member current weight and goal weight
        member.weight = 95.0
        member.goal_weight = 71.0
        member.save()
        print("Updated member goal and start weights.")
        
    except Member.DoesNotExist:
        print(f"Member with email {email} not found.")

if __name__ == "__main__":
    members = Member.objects.all()
    for m in members:
        seed_data(m.user.email)
    if not members:
        print("No members found in system.")
