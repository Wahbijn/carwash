# wash/apps.py
"""
=============================================================================
DJANGO APP CONFIGURATION FOR WASH APP
=============================================================================

This file configures the 'wash' Django app and initializes the automatic
reminder email system when Django starts.

IMPORTANT: The ready() method is called automatically by Django when the
app is loaded. This is where we:
1. Register Django signals
2. Start the APScheduler for reminder emails

=============================================================================
"""

from django.apps import AppConfig


class WashConfig(AppConfig):
    """
    Configuration class for the 'wash' Django application.

    This class is specified in INSTALLED_APPS in settings.py as 'wash'.
    Django automatically finds and uses this configuration.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wash'

    def ready(self):
        """
        Initialize the wash app when Django starts.

        This method is called by Django ONCE when the app is loaded.
        It runs during Django startup, before requests are handled.

        WHAT IT DOES:
        -------------
        1. Import wash.signals module
           - This registers the post_save signal for Booking model
           - The signal will auto-schedule reminders for new bookings

        2. Start the APScheduler
           - Starts background scheduler that runs 24/7
           - Scheduler executes reminder email jobs at scheduled times
           - Jobs are stored in database and survive restarts

        EXECUTION ORDER:
        ----------------
        1. Django starts (python manage.py runserver)
        2. Django loads installed apps
        3. WashConfig.ready() is called
        4. Signals are registered
        5. Scheduler starts
        6. App is ready to handle requests
        7. When bookings are created, signals trigger automatically

        IMPORTANT NOTES:
        ----------------
        - This method can be called multiple times in some Django
          configurations (e.g., with --noreload flag)
        - The scheduler.start() method handles this gracefully
          (won't start twice)
        - If Django is restarted, the scheduler resumes scheduled jobs
          from the database

        TROUBLESHOOTING:
        ----------------
        If you don't see "[OK] APScheduler started successfully" in console:
        - Check for errors in this method
        - Verify django-apscheduler is installed
        - Check INSTALLED_APPS includes 'django_apscheduler'
        """

        # =======================================================================
        # STEP 1: Register Django Signals
        # =======================================================================
        # Import the signals module to register signal handlers
        # This import has a side effect: it registers the @receiver decorator
        # in wash/signals.py with Django's signal system
        import wash.signals

        # =======================================================================
        # STEP 2: Start the APScheduler
        # =======================================================================
        # Import and call start_scheduler() from wash/scheduler.py
        # This starts the background scheduler that runs reminder email jobs
        from wash.scheduler import start_scheduler
        start_scheduler()

        # At this point:
        # - Signals are active and will fire when bookings are saved
        # - Scheduler is running and will execute scheduled jobs
        # - System is ready for automatic reminder emails!
