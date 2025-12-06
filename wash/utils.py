# wash/utils.py
import os
import uuid
from datetime import timezone, timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")


def get_user_email(user):
    """Retourne l'email du user (user.email ou profile.email)."""
    if user is None:
        return None
    email = getattr(user, "email", None)
    if email:
        email = email.strip()
        if email:
            return email
    profile = getattr(user, "profile", None)
    if profile is not None:
        email = getattr(profile, "email", None)
        if email:
            return email.strip() or None
    return None


def make_cancel_token(booking):
    return uuid.uuid4().hex


def _build_ics(booking):
    """
    Fichier .ics pour ajouter la réservation au calendrier.
    Suppose que booking.scheduled_at existe (propriété ou champ).
    """
    start = booking.scheduled_at.astimezone(timezone.utc)
    end = (booking.scheduled_at + timedelta(
        minutes=getattr(booking.service, "duration_minutes", 30)
    )).astimezone(timezone.utc)

    uid = f"booking-{booking.pk}@{settings.DEFAULT_FROM_EMAIL.split('@')[-1]}"

    ics = (
        "BEGIN:VCALENDAR\n"
        "VERSION:2.0\n"
        "PRODID:-//Carwash//EN\n"
        "BEGIN:VEVENT\n"
        f"UID:{uid}\n"
        f"DTSTAMP:{timezone.now().strftime('%Y%m%dT%H%M%SZ')}\n"
        f"DTSTART:{start.strftime('%Y%m%dT%H%M%SZ')}\n"
        f"DTEND:{end.strftime('%Y%m%dT%H%M%SZ')}\n"
        f"SUMMARY:Carwash - {booking.service.name if booking.service else 'Réservation'}\n"
        f"DESCRIPTION:{booking.service.name if booking.service else ''} — "
        f"Véhicule: {getattr(booking.vehicle, 'license_plate', '')}\n"
        "END:VEVENT\n"
        "END:VCALENDAR\n"
    )
    return ics.encode("utf-8")


def send_reminder_email(booking, dry_run=False):
    """
    Envoie un email de rappel stylé (HTML + texte + .ics).
    Utilise les templates:
      - templates/emails/reminder.txt
      - templates/emails/reminder.html
    """
    user = booking.user
    to_email = get_user_email(user)
    if not to_email:
        return False, "no-email"

    site = getattr(settings, "SITE_URL", "http://127.0.0.1:8000").rstrip("/")
    detail_url = f"{site}/bookings/{booking.pk}/"
    cancel_url = f"{site}/bookings/{booking.pk}/cancel/"

    ctx = {
        "user": user,
        "booking": booking,
        "detail_url": detail_url,
        "cancel_url": cancel_url,
        "support_email": getattr(settings, "SUPPORT_EMAIL", "carwashnotifications2@gmail.com"),
    }

    subject = f"Rappel : Réservation #{booking.pk} — {booking.service.name if booking.service else ''}"
    text_body = render_to_string("emails/reminder.txt", ctx)
    html_body = render_to_string("emails/reminder.html", ctx)

    default_from = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@carwash.test")
    from_email = f"CarWash <{default_from}>"

    msg = EmailMultiAlternatives(subject, text_body, from_email, [to_email])

    reply_to = getattr(settings, "SUPPORT_EMAIL", None)
    if reply_to:
        msg.reply_to = [reply_to]

    msg.extra_headers = {
        "List-Unsubscribe": f"<{site}/unsubscribe/>",
        "X-Entity-Ref-ID": f"booking-{booking.pk}",
    }

    msg.attach_alternative(html_body, "text/html")

    # attacher .ics uniquement si booking.scheduled_at existe
    if hasattr(booking, "scheduled_at"):
        try:
            msg.attach(
                f"reservation-{booking.pk}.ics",
                _build_ics(booking),
                "text/calendar",
            )
        except Exception:
            # en dev, on ignore gentiment si ça casse
            pass

    if dry_run:
        print("[dry-run] would send to", to_email, "subject:", subject)
        return True, "dry-run"

    try:
        sent = msg.send(fail_silently=False)
        return bool(sent), None
    except Exception as e:
        return False, str(e)
