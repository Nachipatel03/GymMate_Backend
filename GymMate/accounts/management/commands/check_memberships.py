from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

from accounts.models import MemberMembership, Notification, CustomUser


class Command(BaseCommand):
    help = "Check memberships and create expiry notifications"

    def handle(self, *args, **kwargs):

        today = timezone.now().date()

        # 🔔 3 days before expiry → notify member
        member_notify_date = today + timedelta(days=3)

        expiring_soon = MemberMembership.objects.filter(
            end_date=member_notify_date,
            status="active"
        )

        for membership in expiring_soon:
            Notification.objects.create(
                user=membership.member.user,
                title="Membership Expiring Soon",
                message=f"Your membership will expire on {membership.end_date}. Please renew.",
            )

        # 🔔 1 day before expiry → notify admin
        admin_notify_date = today + timedelta(days=1)

        expiring_for_admin = MemberMembership.objects.filter(
            end_date=admin_notify_date,
            status="active"
        )

        admins = CustomUser.objects.filter(role="ADMIN")

        for membership in expiring_for_admin:
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title="Member Expiring Tomorrow",
                    message=f"{membership.member.full_name}'s membership expires tomorrow.",
                )

        self.stdout.write(self.style.SUCCESS("Membership check completed"))
