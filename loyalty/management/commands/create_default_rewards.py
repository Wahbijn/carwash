from django.core.management.base import BaseCommand
from loyalty.models import Reward


class Command(BaseCommand):
    help = 'Create default loyalty rewards'

    def handle(self, *args, **options):
        rewards_data = [
            {
                'name': 'Lavage Gratuit - Extérieur',
                'description': 'Un lavage extérieur complet offert',
                'points_cost': 50,
                'icon': '🚗',
            },
            {
                'name': 'Réduction 20 TND',
                'description': 'Réduction de 20 TND sur votre prochaine réservation',
                'points_cost': 100,
                'icon': '💰',
            },
            {
                'name': 'Lavage Premium Gratuit',
                'description': 'Un lavage premium complet (intérieur + extérieur)',
                'points_cost': 150,
                'icon': '✨',
            },
            {
                'name': 'Forfait 3 Lavages',
                'description': '3 lavages extérieurs offerts',
                'points_cost': 200,
                'icon': '🎁',
            },
            {
                'name': 'VIP Pass - 1 Mois',
                'description': 'Accès VIP pendant 1 mois avec lavages illimités',
                'points_cost': 500,
                'icon': '👑',
            },
        ]

        created = 0
        for data in rewards_data:
            reward, was_created = Reward.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if was_created:
                created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'+ Created: {reward.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Already exists: {reward.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nDone! Created {created} new rewards.')
        )
