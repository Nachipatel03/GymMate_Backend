from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Payment, MemberMembership

@receiver(post_save, sender=Payment)
def create_membership_after_payment(sender, instance, created, **kwargs):
    if instance.status == "completed" and instance.membership is None:
        member = instance.member
        plan = instance.plan

        membership = MemberMembership.objects.create(
            member=member,
            plan=plan,
            start_date=timezone.now().date(),
            status="active"
        )

        instance.membership = membership
        instance.save(update_fields=["membership"])