# wash/signals.py
"""
=============================================================================
DJANGO SIGNALS FOR AUTOMATIC REMINDER SCHEDULING
=============================================================================

This module uses Django signals to automatically schedule reminder emails
when bookings are created or updated.

WHAT ARE DJANGO SIGNALS?
-------------------------
Django signals are a way to run code automatically when certain events happen.
Think of them like "triggers" in a database.

In our case:
- EVENT: A Booking is saved (created or updated)
- TRIGGER: auto_schedule_reminder() function runs
- ACTION: Email reminder is scheduled automatically

HOW IT WORKS:
-------------
1. User creates a booking through the website
2. Django saves the Booking to database
3. post_save signal fires automatically
4. auto_schedule_reminder() function is called
5. Function checks the booking details
6. Decides whether to send immediately or schedule for later
7. Either sends email now OR schedules it via APScheduler

TWO SCENARIOS:
--------------

Scenario A: Booking is SOON (< 6 hours away)
--------------------------------------------
Example: Current time 13:00, booking at 14:00 (1 hour away)
- Cannot schedule for "6 hours before" (would be 08:00, already passed)
- SOLUTION: Send email IMMEDIATELY when booking is created
- User gets instant confirmation

Scenario B: Booking is FAR (> 6 hours away)
--------------------------------------------
Example: Current time 13:00, booking tomorrow at 14:00
- Can schedule for "6 hours before" (tomorrow at 08:00)
- SOLUTION: Create APScheduler job for tomorrow 08:00
- Email will be sent automatically at that time

SIGNAL REGISTRATION:
--------------------
This signal is registered automatically when Django starts.
See wash/apps.py for the import that activates it.

DEPENDENCIES:
-------------
- wash.scheduler: Contains scheduling functions
- wash.utils: Contains email sending functions
- wash.models: Booking model

CONFIGURATION:
--------------
In settings.py or .env:
    REMINDER_HOURS_BEFORE = 6  # How many hours before booking to send

=============================================================================
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
import logging

from wash.models import Booking

logger = logging.getLogger(__name__)


# =============================================================================
# MAIN SIGNAL HANDLER
# =============================================================================

@receiver(post_save, sender=Booking)
def auto_schedule_reminder(sender, instance, created, **kwargs):
    """
    Automatically schedule or send reminder email when a booking is saved.

    This function is a Django signal receiver. It runs AUTOMATICALLY every time
    a Booking object is saved to the database (created or updated).

    DECORATOR EXPLANATION:
    ----------------------
    @receiver(post_save, sender=Booking)
    - post_save: Signal fires AFTER a model instance is saved
    - sender=Booking: Only fire for Booking model (not other models)
    - This registers the function with Django's signal system

    FUNCTION PARAMETERS:
    --------------------
    - sender: The model class (Booking)
    - instance: The actual Booking object that was saved
    - created: Boolean - True if new booking, False if update
    - **kwargs: Other signal arguments (we don't use them)

    LOGIC FLOW:
    -----------
    1. Check if booking should have a reminder:
       - Not cancelled
       - Reminder not already sent
       - Has scheduled date/time

    2. Calculate time until booking:
       - If < 6 hours: Send email IMMEDIATELY
       - If >= 6 hours: Schedule email for later

    3. For immediate emails:
       - Call send_reminder_email() directly
       - Mark reminder_sent = True
       - Log result

    4. For scheduled emails:
       - Call schedule_booking_reminder()
       - Creates APScheduler job in database
       - Job will run at calculated time

    EXAMPLES:
    ---------
    Example 1: Immediate email
        Time: 13:00
        Create booking for: 14:00 (1 hour away)
        Setting: REMINDER_HOURS_BEFORE = 6
        Result: Email sent NOW (cannot send 6 hours before)

    Example 2: Scheduled email
        Time: 13:00 Monday
        Create booking for: 14:00 Tuesday
        Setting: REMINDER_HOURS_BEFORE = 6
        Result: Email scheduled for Tuesday 08:00

    Example 3: Cancelled booking
        Create booking, then cancel it
        Result: No email sent (skipped)

    Example 4: Update booking
        Update booking time from 14:00 to 15:00
        Result: Old scheduled job removed, new job created for new time
    """

    # Import scheduler functions here to avoid circular imports
    # (scheduler.py imports models, signals.py imports scheduler)
    from wash.scheduler import schedule_booking_reminder
    from wash.utils import send_reminder_email

    # Get the booking object that was just saved
    booking = instance

    # ==========================================================================
    # VALIDATION CHECKS - Skip if booking shouldn't have reminder
    # ==========================================================================

    # Check 1: Skip cancelled bookings
    # We don't send reminders for cancelled appointments
    if booking.status == 'cancelled':
        logger.info(f"Booking #{booking.pk} is cancelled - not scheduling reminder")
        return

    # Check 2: Skip if reminder already sent
    # Prevents duplicate emails when booking is updated
    if booking.reminder_sent:
        logger.info(f"Booking #{booking.pk} reminder already sent - not rescheduling")
        return

    # Check 3: Skip if no scheduled time
    # Can't send reminder if we don't know when booking is!
    if not booking.scheduled_at:
        logger.info(f"Booking #{booking.pk} has no scheduled time - not scheduling reminder")
        return

    # ==========================================================================
    # CONFIGURATION - Get reminder hours from settings
    # ==========================================================================

    # Get how many hours before booking to send reminder
    # Default: 6 hours (can be changed in .env or settings.py)
    hours_before = getattr(settings, 'REMINDER_HOURS_BEFORE', 6)

    # ==========================================================================
    # DECISION LOGIC - Send now or schedule for later?
    # ==========================================================================

    # Calculate how many hours until the booking
    now = timezone.now()
    time_until_booking = (booking.scheduled_at - now).total_seconds() / 3600  # Convert to hours

    # ==========================================================================
    # SCENARIO A: Booking is SOON - Send email IMMEDIATELY
    # ==========================================================================

    # If booking is less than "hours_before" away, we can't schedule
    # for that time (it would be in the past).
    # Solution: Send the reminder email RIGHT NOW!

    if time_until_booking < hours_before and time_until_booking > 0:
        logger.info(
            f"[AUTO] Booking #{booking.pk} is in {time_until_booking:.1f} hours "
            f"(< {hours_before} hours) - sending reminder NOW"
        )

        # Send the email immediately
        ok, error = send_reminder_email(booking, dry_run=False)

        if ok:
            # Email sent successfully!
            # Mark as sent so we don't send again
            booking.reminder_sent = True
            booking.save(update_fields=['reminder_sent'])
            logger.info(f"[AUTO] Sent IMMEDIATE reminder for booking #{booking.pk}")
        else:
            # Email failed to send
            logger.error(f"[AUTO] Failed to send immediate reminder: {error}")

        # We're done - email was sent immediately
        return

    # ==========================================================================
    # SCENARIO B: Booking is FAR - Schedule email for later
    # ==========================================================================

    # Booking is far enough in the future that we can schedule
    # a reminder for "hours_before" before it.
    # Example: Booking tomorrow at 14:00, schedule email for tomorrow at 08:00

    success = schedule_booking_reminder(booking, hours_before=hours_before)

    if success:
        # Job was successfully created and saved to database
        if created:
            logger.info(f"[AUTO] Scheduled reminder for NEW booking #{booking.pk}")
        else:
            logger.info(f"[AUTO] Rescheduled reminder for UPDATED booking #{booking.pk}")
    else:
        # Failed to create scheduled job
        # This might happen if booking time is in the past
        logger.warning(f"[AUTO] Failed to schedule reminder for booking #{booking.pk}")


# =============================================================================
# ADDITIONAL NOTES
# =============================================================================

"""
DATABASE TABLES:
----------------
This signal doesn't create tables itself, but uses these tables:
- wash_booking: Where bookings are stored
- django_apscheduler_djangojob: Where scheduled jobs are stored
- django_apscheduler_djangojobexecution: Job execution history

TESTING:
--------
To test this signal:
1. Start Django: python manage.py runserver
2. Create a booking through the website
3. Watch Django console for log messages
4. Check scheduled jobs: python check_jobs.py

TROUBLESHOOTING:
----------------
If emails aren't being sent:
1. Check Django console for error messages
2. Verify REMINDER_HOURS_BEFORE in settings
3. Check email credentials in .env
4. Verify booking has scheduled_date and scheduled_time
5. Run: python manage.py shell
   >>> from wash.models import Booking
   >>> b = Booking.objects.latest('id')
   >>> print(b.scheduled_at, b.reminder_sent, b.status)

SIGNAL REGISTRATION:
--------------------
This signal is activated when wash/apps.py imports this module.
See WashConfig.ready() in wash/apps.py.
"""
