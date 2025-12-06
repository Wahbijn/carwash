# accounts/management/commands/copy_profile_emails.py
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.apps import apps

User = get_user_model()

class Command(BaseCommand):
    help = "Copy email addresses from accounts.Profile.email into User.email for users that have none."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Do not save changes; only show what would be done.'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing user.email with profile.email.'
        )
        parser.add_argument(
            '--commit-batch',
            type=int,
            default=100,
            help='How many users to process per DB transaction (default: 100).'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        batch = options['commit_batch']

        # check Profile model exists
        try:
            Profile = apps.get_model('accounts', 'Profile')
        except LookupError:
            raise CommandError(
                "accounts.Profile model not found. Create it or adapt this script."
            )

        qs = User.objects.all().select_related('profile')
        total = qs.count()
        if total == 0:
            self.stdout.write("No users found. Nothing to do.")
            return

        changed = 0
        skipped = 0
        overwritten = 0
        errors = 0

        self.stdout.write(f"Found {total} users; dry_run={dry_run}; force={force}")

        users = list(qs)  # evaluate once
        i = 0
        while i < len(users):
            chunk = users[i:i+batch]
            i += batch
            if not dry_run:
                tx = transaction.atomic()
                tx.__enter__()

            try:
                for u in chunk:
                    p = getattr(u, 'profile', None)
                    profile_email = getattr(p, 'email', None) if p is not None else None
                    if not profile_email:
                        skipped += 1
                        self.stdout.write(f"User {u.pk} ({u.username}) — profile.email empty (skipped)")
                        continue

                    user_email = (u.email or "").strip()
                    profile_email = profile_email.strip()

                    if user_email:
                        if force:
                            if user_email != profile_email:
                                if not dry_run:
                                    u.email = profile_email
                                    u.save(update_fields=['email'])
                                overwritten += 1
                                self.stdout.write(f"User {u.pk} ({u.username}) — overwritten: {user_email} -> {profile_email}")
                            else:
                                skipped += 1
                                self.stdout.write(f"User {u.pk} ({u.username}) — same email (skipped)")
                        else:
                            skipped += 1
                            self.stdout.write(f"User {u.pk} ({u.username}) — already has email (use --force to overwrite)")
                        continue

                    # user has no email — copy it
                    if not dry_run:
                        u.email = profile_email
                        u.save(update_fields=['email'])
                    changed += 1
                    self.stdout.write(f"User {u.pk} ({u.username}) — copied profile.email -> {profile_email}")

                if not dry_run:
                    tx.__exit__(None, None, None)
            except Exception as e:
                errors += 1
                if not dry_run:
                    tx.__exit__(type(e), e, e.__traceback__)
                self.stderr.write(f"Error while processing batch starting at {i-batch}: {e}")

        self.stdout.write("=== Summary ===")
        self.stdout.write(f"Total users checked: {total}")
        self.stdout.write(f"Copied emails: {changed}")
        self.stdout.write(f"Overwritten (with --force): {overwritten}")
        self.stdout.write(f"Skipped: {skipped}")
        if errors:
            self.stderr.write(f"Errors during operation: {errors}")

        if dry_run:
            self.stdout.write("Dry-run mode: no database changes were made.")
