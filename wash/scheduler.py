# wash/scheduler.py
"""
=============================================================================
AUTOMATIC EMAIL REMINDER SCHEDULER
=============================================================================

This module handles the automatic scheduling and sending of reminder emails
for car wash bookings using APScheduler (Advanced Python Scheduler).

HOW IT WORKS:
-------------
1. When Django starts, this scheduler starts automatically (see wash/apps.py)
2. When a booking is created, a signal triggers (see wash/signals.py)
3. The signal calls schedule_booking_reminder() to create a scheduled job
4. The job is stored in the database (django_apscheduler tables)
5. At the scheduled time, send_booking_reminder() runs automatically
6. The reminder email is sent to the user

EXAMPLE:
--------
- Booking created for: Tomorrow at 14:00 (2 PM)
- Reminder setting: 6 hours before
- Job scheduled for: Tomorrow at 08:00 (8 AM)
- At 08:00 tomorrow: Email is sent automatically

COMPONENTS:
-----------
- scheduler: Background scheduler that runs 24/7 with Django
- send_booking_reminder(): Function that runs at scheduled time to send email
- schedule_booking_reminder(): Function to create a new scheduled job
- start_scheduler(): Starts the scheduler when Django starts
- stop_scheduler(): Stops the scheduler when Django shuts down

DEPENDENCIES:
-------------
- APScheduler: Python scheduling library
- django-apscheduler: Django integration for APScheduler
- wash.utils.send_reminder_email: Function that sends the actual email

CONFIGURATION:
--------------
In settings.py:
    REMINDER_HOURS_BEFORE = 6  # How many hours before booking to send reminder

In .env:
    REMINDER_HOURS_BEFORE=6

=============================================================================
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone
from django.conf import settings
import logging

from wash.models import Booking
from wash.utils import send_reminder_email

logger = logging.getLogger(__name__)

# =============================================================================
# SCHEDULER INITIALIZATION
# =============================================================================

# Create a global BackgroundScheduler instance
# BackgroundScheduler runs in a separate thread and doesn't block Django
scheduler = BackgroundScheduler()

# Add DjangoJobStore so jobs are saved to database
# This means scheduled jobs survive Django restarts!
scheduler.add_jobstore(DjangoJobStore(), "default")


# =============================================================================
# JOB FUNCTION (Runs at scheduled time)
# =============================================================================

def send_booking_reminder(booking_id):
    """
    Send a reminder email for a specific booking.

    This function is called by APScheduler at the scheduled time.
    It runs automatically without any manual intervention.

    PROCESS:
    --------
    1. Fetch the booking from database by ID
    2. Check if reminder was already sent (safety check)
    3. Check if booking was cancelled (don't send if cancelled)
    4. Call send_reminder_email() to send the actual email
    5. Mark booking.reminder_sent = True
    6. Log success or failure

    Args:
        booking_id (int): The ID of the Booking object to send reminder for

    Returns:
        None (logs results instead)

    Example:
        When this runs at 08:00 for booking #123:
        - Fetches Booking #123 from database
        - Sends email to user's email address
        - Sets booking.reminder_sent = True
        - Logs: "[OK] Sent reminder for booking #123"
    """
    try:
        # Fetch the booking from database
        booking = Booking.objects.get(pk=booking_id)

        # Safety check: Skip if reminder already sent
        if booking.reminder_sent:
            logger.info(f"Skipping booking #{booking_id} - reminder already sent")
            return

        # Safety check: Skip if booking is cancelled
        if booking.status == 'cancelled':
            logger.info(f"Skipping booking #{booking_id} - booking is cancelled")
            return

        # Send the reminder email
        # send_reminder_email() is defined in wash/utils.py
        # It handles email construction, SMTP sending, attachments, etc.
        ok, error = send_reminder_email(booking, dry_run=False)

        if ok:
            # Email sent successfully
            # Mark reminder as sent so we don't send again
            booking.reminder_sent = True
            booking.save(update_fields=['reminder_sent'])
            logger.info(f"[OK] Sent reminder for booking #{booking_id}")
        else:
            # Email failed to send
            logger.error(f"[ERROR] Failed to send reminder for booking #{booking_id}: {error}")

    except Booking.DoesNotExist:
        # Booking was deleted before reminder was sent
        logger.error(f"Booking #{booking_id} not found - may have been deleted")
    except Exception as e:
        # Any other unexpected error
        logger.error(f"Error sending reminder for booking #{booking_id}: {str(e)}")


# =============================================================================
# SCHEDULING FUNCTION (Creates jobs)
# =============================================================================

def schedule_booking_reminder(booking, hours_before=6):
    """
    Schedule a reminder email to be sent X hours before the booking time.

    This is called by the Django signal when a booking is created/updated.
    It creates a scheduled job that will run at the calculated time.

    PROCESS:
    --------
    1. Calculate when to send reminder: booking_time - hours_before
    2. Check if reminder time is in the future (can't schedule past times)
    3. Create a unique job ID based on booking ID
    4. Remove any existing job for this booking (in case of updates)
    5. Create new APScheduler job with DateTrigger
    6. Job is saved to database automatically
    7. At the scheduled time, send_booking_reminder() will run

    Args:
        booking (Booking): The Booking object to schedule reminder for
        hours_before (int): How many hours before booking to send (default: 6)

    Returns:
        bool: True if successfully scheduled, False if failed

    Example 1 (Future booking):
        booking.scheduled_at = "2026-01-05 14:00"
        hours_before = 6
        → reminder_time = "2026-01-05 08:00"
        → Job created to run at 08:00 tomorrow
        → Returns True

    Example 2 (Past reminder time):
        Current time = "2026-01-04 13:00"
        booking.scheduled_at = "2026-01-04 14:00"
        hours_before = 6
        → reminder_time = "2026-01-04 08:00" (already passed!)
        → Cannot schedule
        → Returns False
    """

    # Check if booking has a scheduled time
    if not booking.scheduled_at:
        logger.warning(f"Booking #{booking.pk} has no scheduled_at time - cannot schedule reminder")
        return False

    # Calculate when to send the reminder
    # scheduled_at is a timezone-aware datetime
    # timedelta(hours=6) subtracts 6 hours
    reminder_time = booking.scheduled_at - timezone.timedelta(hours=hours_before)

    # Get current time (timezone-aware)
    now = timezone.now()

    # Check if reminder time is in the past
    # We can't schedule jobs for past times!
    if reminder_time <= now:
        logger.warning(
            f"Booking #{booking.pk} reminder time ({reminder_time}) is in the past, "
            f"cannot schedule (current time: {now})"
        )
        return False

    # Create a unique job ID based on booking ID
    # Format: "booking_reminder_123"
    # This allows us to find and update/delete the job later
    job_id = f"booking_reminder_{booking.pk}"

    # Remove existing job if it exists
    # This happens when a booking is updated and needs rescheduling
    try:
        scheduler.remove_job(job_id)
        logger.info(f"Removed existing job for booking #{booking.pk}")
    except:
        # No existing job, that's fine
        pass

    # Schedule the job
    try:
        scheduler.add_job(
            # Function to call at scheduled time
            send_booking_reminder,

            # Use DateTrigger to run once at specific time
            trigger=DateTrigger(run_date=reminder_time),

            # Arguments to pass to send_booking_reminder()
            args=[booking.pk],

            # Unique ID for this job
            id=job_id,

            # Replace if job with same ID exists
            replace_existing=True,

            # Human-readable name (for debugging)
            name=f"Reminder for Booking #{booking.pk}"
        )

        logger.info(
            f"[OK] Scheduled reminder for Booking #{booking.pk} "
            f"at {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return True

    except Exception as e:
        logger.error(f"Error scheduling reminder for booking #{booking.pk}: {str(e)}")
        return False


# =============================================================================
# SCHEDULER LIFECYCLE MANAGEMENT
# =============================================================================

def start_scheduler():
    """
    Start the APScheduler if it's not already running.

    This is called automatically when Django starts (see wash/apps.py).
    The scheduler runs in a background thread and checks for jobs to execute.

    IMPORTANT:
    ----------
    The scheduler must be running for jobs to execute!
    If Django is stopped, scheduled jobs won't run.
    For production, use a process manager (systemd, supervisor, etc.)
    to keep Django running 24/7.

    Example:
        Django starts → apps.py calls start_scheduler()
        → Scheduler starts in background thread
        → Watches for jobs to execute
        → Runs send_booking_reminder() at scheduled times
    """
    if not scheduler.running:
        scheduler.start()
        logger.info("[OK] APScheduler started successfully")
    else:
        logger.info("APScheduler is already running")


def stop_scheduler():
    """
    Stop the APScheduler gracefully.

    This is called when Django shuts down.
    It ensures all running jobs complete before stopping.

    Note: Scheduled jobs remain in database and will resume
    when scheduler starts again.
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped")
