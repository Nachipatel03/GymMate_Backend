from django.core.mail import send_mail
from django.conf import settings
import logging
import threading

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def _send_email_thread(subject, message, from_email, recipient_list):
        """
        Helper method to run send_mail in a background thread.
        """
        try:
            send_mail(subject, message, from_email, recipient_list)
            logger.info(f"Email sent successfully to {recipient_list}")
        except Exception as e:
            logger.error(f"Background email sending failed: {str(e)}")

    @staticmethod
    def send_welcome_email(email, full_name, password):
        """
        Sends a welcome email to a newly created member with their login credentials.
        """
        subject = "Welcome to GymMate! Your Account Credentials"
        message = (
            f"Hello {full_name},\n\n"
            f"Welcome to GymMate! Your account has been created successfully.\n\n"
            f"You can log in using the following credentials:\n"
            f"Email: {email}\n"
            f"Password: {password}\n\n"
            f"Please log in and change your password for security purposes.\n\n"
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
        subject = "Your GymMate Account is Actived!"
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
