from django.db import transaction
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from accounts.models import (
    MemberMembership,
    MembershipPlan,
    Member,
    Payment,
    Notification,
    CustomUser,
)


class MembershipService:

    # ------------------------------------------------------
    # 🔔 ADMIN NOTIFICATION HELPER
    # ------------------------------------------------------
    @staticmethod
    def notify_admins(title, message):
        admins = CustomUser.objects.filter(role="ADMIN")

        for admin in admins:
            Notification.objects.create(
                user=admin,
                type="admin",
                title=title,
                message=message
            )

    # ------------------------------------------------------
    # ✅ ACTIVATE MEMBERSHIP
    # ------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def activate_membership(member: Member, plan: MembershipPlan, payment_method="cash"):

        # 1️⃣ Expire old active membership
        MemberMembership.objects.filter(
            member=member,
            status="active"
        ).update(status="expired")

        start_date = timezone.now().date()
        end_date = start_date + relativedelta(months=plan.duration_months)

        # 2️⃣ Create new membership
        membership = MemberMembership.objects.create(
            member=member,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            status="active"
        )

        # 3️⃣ Create payment
        invoice_number = f"INV-{int(timezone.now().timestamp())}"

        Payment.objects.create(
            member=member,
            membership=membership,
            amount=plan.price,
            payment_date=start_date,
            payment_method=payment_method,
            status="completed",
            invoice_number=invoice_number
        )
        
        # Activate user on first payment
        if not member.user.is_verified:
            member.user.is_verified = True
            member.user.is_active = True
            member.user.save()

        if member.status != "active":
            member.status = "active"
            member.save()

        # 4️⃣ Notify Member
        Notification.objects.create(
            user=member.user,
            type="member",
            title="Membership Activated",
            message=f"Your {plan.name} membership is active until {end_date}."
        )

        # 5️⃣ Notify Admins
        MembershipService.notify_admins(
            title="New Membership Activated",
            message=f"{member.full_name} activated {plan.name} plan. Amount ₹{plan.price}."
        )

        return membership

    # ------------------------------------------------------
    # 🔄 RENEW MEMBERSHIP
    # ------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def renew_membership(member: Member, payment_method="cash"):

        active_membership = MemberMembership.objects.filter(
            member=member,
            status="active"
        ).first()

        if not active_membership:
            raise Exception("No active membership found.")

        plan = active_membership.plan

        new_end_date = active_membership.end_date + relativedelta(
            months=plan.duration_months
        )

        active_membership.end_date = new_end_date
        active_membership.save()

        invoice_number = f"INV-{int(timezone.now().timestamp())}"

        Payment.objects.create(
            member=member,
            membership=active_membership,
            amount=plan.price,
            payment_date=timezone.now().date(),
            payment_method=payment_method,
            status="completed",
            invoice_number=invoice_number
        )

        # Notify Member
        Notification.objects.create(
            user=member.user,
            type="member",
            title="Membership Renewed",
            message=f"Your membership has been renewed until {new_end_date}."
        )

        # Notify Admins
        MembershipService.notify_admins(
            title="Membership Renewed",
            message=f"{member.full_name} renewed membership. Amount ₹{plan.price}."
        )

        return active_membership

    # ------------------------------------------------------
    # ❌ CANCEL MEMBERSHIP
    # ------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def cancel_membership(member: Member):

        active_membership = MemberMembership.objects.filter(
            member=member,
            status="active"
        ).first()

        if not active_membership:
            return None

        active_membership.status = "cancelled"
        active_membership.save()

        # Notify Member
        Notification.objects.create(
            user=member.user,
            type="member",
            title="Membership Cancelled",
            message="Your membership has been cancelled."
        )

        # Notify Admins
        MembershipService.notify_admins(
            title="Membership Cancelled",
            message=f"{member.full_name} cancelled their membership."
        )

        return active_membership

    # ------------------------------------------------------
    # ⏳ AUTO EXPIRE (CRON)
    # ------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def expire_memberships():

        today = timezone.now().date()

        expired_memberships = MemberMembership.objects.filter(
            end_date__lt=today,
            status="active"
        )

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
            MembershipService.notify_admins(
                title="Member Membership Expired",
                message=f"{membership.member.full_name}'s membership has expired."
            )

        return expired_memberships.count()