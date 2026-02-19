from datetime import timedelta
from django.utils import timezone
from .models import MemberMembership,Notification,CustomUser 

def check_membership_expiry():

    today = timezone.now().date()

    
    notify_members = MemberMembership.objects.filter(
        end_date=today + timedelta(days=4),
        status="active"
    )

    for membership in notify_members:
        Notification.objects.create(
            user=membership.member.user,
            title="Membership Expiring Soon",
            message="Your membership will expire in 4 days. Please renew."
        )

    # 1 day before expiry (Admin notification)
    notify_admin = MemberMembership.objects.filter(
        end_date=today + timedelta(days=1),
        status="active"
    )

    admin_users = CustomUser.objects.filter(role="ADMIN")

    for membership in notify_admin:
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                title="Membership Expiring Tomorrow",
                message=f"{membership.member.full_name}'s membership expires tomorrow."
            )

    # Auto expire
    expired = MemberMembership.objects.filter(
        end_date__lt=today,
        status="active"
    )

    expired.update(status="expired")