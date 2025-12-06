# wash/management/commands/send_reminders.py
from django.core.management.base import BaseCommand
from django.utils import timezone

from wash.models import Booking
from wash.utils import send_reminder_email


class Command(BaseCommand):
    help = "Envoie les emails de rappel pour les réservations à venir."

    def add_arguments(self, parser):
        parser.add_argument("--minutes", type=int, default=None)
        parser.add_argument("--hours", type=int, default=None)
        parser.add_argument("--dry-run", action="store_true", default=False)

    def handle(self, *args, **options):
        minutes = options["minutes"]
        hours = options["hours"]
        dry_run = options["dry_run"]

        if minutes is None and hours is None:
            self.stderr.write("Specify --minutes or --hours")
            return

        if minutes is not None:
            window_seconds = minutes * 60
        else:
            if hours > 24:
                self.stderr.write("Doit être inférieur ou égal à 24 heures")
                return
            window_seconds = hours * 3600

        tz = timezone.get_current_timezone()
        now = timezone.localtime(timezone.now(), tz)
        window_to = now + timezone.timedelta(seconds=window_seconds)

        self.stdout.write(
            f"Now(local)={now.isoformat()} window_to={window_to.isoformat()} "
            f"(window_seconds={window_seconds})"
        )

        qs = (
            Booking.objects
            .select_related("user", "service", "vehicle")
            .filter(scheduled_date__isnull=False, scheduled_time__isnull=False)
            .order_by("scheduled_date", "scheduled_time")
        )

        checked = 0
        sent = 0

        for booking in qs:
            checked += 1

            # reconstruire un datetime local à partir de la date+heure
            scheduled_naive = timezone.datetime.combine(
                booking.scheduled_date, booking.scheduled_time
            )
            scheduled_local = timezone.make_aware(scheduled_naive, tz)

            if getattr(booking, "reminder_sent", False):
                self.stdout.write(
                    f"Booking {booking.pk} reminder_sent already (skipped)"
                )
                continue

            if scheduled_local < now:
                self.stdout.write(
                    f"Booking {booking.pk} scheduled_local={scheduled_local.isoformat()} "
                    f"now={now.isoformat()} -> already in past (skipped)"
                )
                continue

            if scheduled_local > window_to:
                self.stdout.write(
                    f"Booking {booking.pk} scheduled_local={scheduled_local.isoformat()} "
                    f"now={now.isoformat()} -> outside window (skipped)"
                )
                continue

            ok, error = send_reminder_email(booking, dry_run=dry_run)
            if ok:
                if not dry_run and hasattr(booking, "reminder_sent"):
                    Booking.objects.filter(pk=booking.pk).update(reminder_sent=True)
                sent += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Sent reminder for booking {booking.pk} -> {booking.user.email}"
                    )
                )
            else:
                self.stderr.write(
                    f"Error sending booking {booking.pk}: {error or 'unknown'}"
                )

        self.stdout.write(f"Checked: {checked}; Rappels envoyés : {sent}")
