from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from accounts.models import MemberMembership, Notification, CustomUser


class Command(BaseCommand):
    help = "Check memberships and create expiry notifications"

    def handle(self, *args, **kwargs):

        today = timezone.now().date()

        # --------------------------------------------------
        # 1️⃣ EXPIRE MEMBERSHIPS
        # --------------------------------------------------
        expired_memberships = MemberMembership.objects.filter(
            end_date__lt=today,
            status="active"
        )

        admins = CustomUser.objects.filter(role="ADMIN")

        for membership in expired_memberships:
            membership.status = "expired"
            membership.save()

            # Notify Member
            Notification.objects.create(
                user=membership.member.user,
                type="member",
                title="Membership Expired",
                message="Your membership has expired. Please renew."
            )

            # Notify Admins
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    type="admin",
                    title="Member Membership Expired",
                    message=f"{membership.member.full_name}'s membership has expired."
                )

        # --------------------------------------------------
        # 2️⃣ 3 DAYS BEFORE EXPIRY → MEMBER
        # --------------------------------------------------
        member_notify_date = today + timedelta(days=3)

        expiring_soon = MemberMembership.objects.filter(
            end_date=member_notify_date,
            status="active"
        )

        for membership in expiring_soon:

            # Prevent duplicate reminder
            if not Notification.objects.filter(
                user=membership.member.user,
                title="Membership Expiring Soon",
                message__icontains=str(membership.end_date)
            ).exists():

                Notification.objects.create(
                    user=membership.member.user,
                    type="member",
                    title="Membership Expiring Soon",
                    message=f"Your membership will expire on {membership.end_date}. Please renew."
                )

        # --------------------------------------------------
        # 3️⃣ 1 DAY BEFORE EXPIRY → ADMIN
        # --------------------------------------------------
        admin_notify_date = today + timedelta(days=3)

        expiring_for_admin = MemberMembership.objects.filter(
            end_date=admin_notify_date,
            status="active"
        )

        for membership in expiring_for_admin:
            for admin in admins:

                if not Notification.objects.filter(
                    user=admin,
                    title="Member Expiring Tomorrow",
                    message__icontains=membership.member.full_name
                ).exists():

                    Notification.objects.create(
                        user=admin,
                        type="admin",
                        title="Member Expiring Tomorrow",
                        message=f"{membership.member.full_name}'s membership expires tomorrow."
                    )

        self.stdout.write(self.style.SUCCESS("Membership check completed"))