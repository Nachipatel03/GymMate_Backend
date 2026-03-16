from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

def check_memberships_task():
    """Task to run the check_memberships management command."""
    from datetime import datetime
    now = datetime.now()
    logger.info(f"Triggering check_memberships cron job at {now}...")
    try:
        call_command("check_memberships")
        logger.info(f"Successfully completed check_memberships cron job at {now}.")
    except Exception as e:
        logger.error(f"Error running check_memberships cron job at {now}: {e}")

def start():
    """Initialize and start the background scheduler."""
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Schedule the task to run once a day at midnight (00:00)
    scheduler.add_job(
        check_memberships_task,
        trigger="cron",
        hour=0,
        minute=0,
        id="check_memberships_daily",
        max_instances=1,
        replace_existing=True,
    )

    register_events(scheduler)
    scheduler.start()
    logger.info("Scheduler started successfully.")
