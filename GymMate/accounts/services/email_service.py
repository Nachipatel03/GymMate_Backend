from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
import logging
import threading

logger = logging.getLogger(__name__)


def get_template_from_db(slug):
    """Try to load an email template from the database. Returns (subject, html_body) or (None, None)."""
    try:
        from accounts.models import EmailTemplate
        tpl = EmailTemplate.objects.filter(slug=slug).first()
        if tpl:
            return tpl.subject, tpl.html_body
    except Exception:
        pass
    return None, None

class EmailService:
    @staticmethod
    def _send_email_thread(subject, message, from_email, recipient_list, html_message=None):
        """
        Helper method to run send_mail in a background thread.
        """
        try:
            logger.info(f"Attempting to send email from '{from_email}' to {recipient_list} with subject '{subject}'")
            if html_message:
                email = EmailMultiAlternatives(subject, message, from_email, recipient_list)
                email.attach_alternative(html_message, "text/html")
                email.send()
            else:
                send_mail(subject, message, from_email, recipient_list)
            logger.info(f"Email sent successfully to {recipient_list}")
        except Exception as e:
            logger.error(f"Background email sending failed: {str(e)}")

    @staticmethod
    def send_welcome_email(email, full_name, password):
        """
        Sends a welcome email to a newly created member with their login credentials using an HTML template.
        """
        from accounts.models import CustomUser
        
        # Fetch admin contact info for support
        admin = CustomUser.objects.filter(role="ADMIN", is_active=True).first()
        support_email = admin.email if admin else "support@gymmate.com"
        support_phone = admin.phone if admin and admin.phone else "+1234567890"

        subject = "Welcome to GymMate! Your Account Credentials"
        
        context = {
            'MemberName': full_name,
            'MemberEmail': email,
            'TemporaryPassword': password,
            'LoginURL': getattr(settings, 'FRONTEND_URL', 'http://localhost:5173') + '/login',
            'SupportEmail': support_email,
            'SupportPhone': support_phone,
            'Year': timezone.now().year
        }

        # Try loading from database first
        db_subject, db_html = get_template_from_db('member_welcome')
        if db_html:
            subject = db_subject or subject
            from django.template import Template, Context
            html_message = Template(db_html).render(Context(context))
        else:
            html_message = render_to_string('emails/member_creation_email.html', context)

        plain_message = strip_tags(html_message)
        
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        threading.Thread(
            target=EmailService._send_email_thread,
            args=(subject, plain_message, from_email, recipient_list, html_message)
        ).start()
        
        return True

    @staticmethod
    def send_activation_email(email, full_name, plan_name, start_date, end_date):
        """
        Sends an email to a member when their account is activated and plan is assigned.
        """
        subject = "Welcome to GymMate! Your Account is Activated"
        message = (
            f"Hello {full_name},\n\n"
            f"Great news! Your account at GymMate has been activated.\n\n"
            f"Your membership details:\n"
            f"Plan: {plan_name}\n"
            f"Start Date: {start_date}\n"
            f"End Date: {end_date}\n\n"
            f"You can now log in and start your fitness journey!\n\n"
            f"Best regards,\n"
            f"The GymMate Team"
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        threading.Thread(
            target=EmailService._send_email_thread,
            args=(subject, message, from_email, recipient_list)
        ).start()

        return True

    @staticmethod
    def send_account_activation_email(email, full_name):
        """
        Sends an email to a member when their account is activated without a specific plan.
        """
        subject = "Your GymMate Account is Activated!"
        message = (
            f"Hello {full_name},\n\n"
            f"Great news! Your account at GymMate has been activated by the admin.\n\n"
            f"You can now log in and access your member dashboard.\n\n"
            f"Best regards,\n"
            f"The GymMate Team"
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        threading.Thread(
            target=EmailService._send_email_thread,
            args=(subject, message, from_email, recipient_list)
        ).start()

        return True

    @staticmethod
    def send_account_inactivation_email(email, full_name):
        """
        Sends an email to a member when their account is inactivated or deleted.
        """
        subject = "Notice: Your GymMate Account Status"
        message = (
            f"Hello {full_name},\n\n"
            f"This is a notification that your GymMate account has been deactivated.\n\n"
            f"If you believe this is a mistake or have any questions, please contact the administration.\n\n"
            f"Best regards,\n"
            f"The GymMate Team"
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        threading.Thread(
            target=EmailService._send_email_thread,
            args=(subject, message, from_email, recipient_list)
        ).start()

        return True
