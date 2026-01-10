#!/usr/bin/env python
"""
=============================================================================
CHECK SCHEDULED REMINDER JOBS
=============================================================================

This utility script displays all scheduled reminder email jobs.

WHAT IT DOES:
-------------
- Connects to the Django database
- Queries the django_apscheduler_djangojob table
- Shows all scheduled reminder jobs with timing information
- Helps verify that emails are scheduled correctly

WHEN TO USE:
------------
- After creating a booking to verify reminder was scheduled
- To see when upcoming reminders will be sent
- To troubleshoot if emails aren't being sent
- To monitor the automatic reminder system

USAGE:
------
python check_jobs.py

EXAMPLE OUTPUT:
--------------
============================================================
Current time: 2026-01-04 13:30:00
============================================================

Scheduled Jobs: 2

[PENDING] Job: booking_reminder_125
  Next run: 14:00:00
  In: 30.0 minutes

[PENDING] Job: booking_reminder_126
  Next run: 08:00:00
  In: 1110.0 minutes

============================================================

UNDERSTANDING THE OUTPUT:
-------------------------
- [PENDING]: Job is scheduled and waiting to run
- [OVERDUE]: Job should have run but didn't (scheduler might have been stopped)
- Next run: Local time when the job will execute
- In: X minutes: How long until the job runs

TROUBLESHOOTING:
----------------
No jobs found:
- Bookings might all be less than 6 hours away (sent immediately)
- Or no bookings have been created yet

Jobs showing [OVERDUE]:
- Django was stopped when the job should have run
- Restart Django and the job will run immediately

Job missing:
- Check if reminder was already sent (booking.reminder_sent = True)
- Check if booking was cancelled

=============================================================================
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carwash_project.settings')
django.setup()

from django_apscheduler.models import DjangoJob
from django.utils import timezone

# Get all scheduled jobs from database
jobs = DjangoJob.objects.all()
now = timezone.now()

# Display current time
print(f'\n{"="*60}')
print(f'Current time: {now.strftime("%Y-%m-%d %H:%M:%S")}')
print(f'{"="*60}\n')

# Check if any jobs are scheduled
if jobs.count() == 0:
    print('No scheduled jobs found.')
    print('\nThis is normal if:')
    print('- All bookings are less than 6 hours away (emails sent immediately)')
    print('- No bookings have been created yet')
    print('- All reminders have already been sent\n')
else:
    print(f'Scheduled Jobs: {jobs.count()}\n')

    # Display each job
    for job in jobs:
        job_id = job.id
        next_run = job.next_run_time

        if next_run:
            # Calculate time until job runs
            diff_minutes = (next_run - now).total_seconds() / 60

            if diff_minutes > 0:
                # Job is in the future - will run normally
                print(f'[PENDING] Job: {job_id}')
                print(f'  Next run: {next_run.strftime("%Y-%m-%d %H:%M:%S")}')
                print(f'  In: {diff_minutes:.1f} minutes')

                # Show hours if more than 60 minutes
                if diff_minutes > 60:
                    diff_hours = diff_minutes / 60
                    print(f'       ({diff_hours:.1f} hours)')
                print()
            else:
                # Job is overdue - should have run already
                print(f'[OVERDUE] Job: {job_id}')
                print(f'  Should have run at: {next_run.strftime("%Y-%m-%d %H:%M:%S")}')
                print(f'  Overdue by: {abs(diff_minutes):.1f} minutes')
                print(f'  (Will run when Django starts)\n')

print(f'{"="*60}\n')
