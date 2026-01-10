from django.core.management.base import BaseCommand
from badges.models import Badge


class Command(BaseCommand):
    help = 'Create default achievement badges'

    def handle(self, *args, **options):
        badges_data = [
            # Booking count badges
            {'name': 'Premier Pas', 'description': 'Première réservation effectuée', 'icon': '🌟', 'rarity': 'common', 'condition_type': 'total_bookings', 'condition_value': 1},
            {'name': 'Habitué', 'description': '5 réservations effectuées', 'icon': '⭐', 'rarity': 'common', 'condition_type': 'total_bookings', 'condition_value': 5},
            {'name': 'Client VIP', 'description': '10 réservations effectuées', 'icon': '💫', 'rarity': 'rare', 'condition_type': 'total_bookings', 'condition_value': 10},
            {'name': 'Super Client', 'description': '25 réservations effectuées', 'icon': '🌠', 'rarity': 'epic', 'condition_type': 'total_bookings', 'condition_value': 25},
            {'name': 'Légende', 'description': '50 réservations effectuées!', 'icon': '👑', 'rarity': 'legendary', 'condition_type': 'total_bookings', 'condition_value': 50},
            
            # Completed bookings
            {'name': 'Première Victoire', 'description': 'Première réservation complétée', 'icon': '✅', 'rarity': 'common', 'condition_type': 'completed_bookings', 'condition_value': 1},
            {'name': 'Fidèle', 'description': '10 lavages complétés', 'icon': '🏅', 'rarity': 'rare', 'condition_type': 'completed_bookings', 'condition_value': 10},
            {'name': 'Champion', 'description': '20 lavages complétés', 'icon': '🏆', 'rarity': 'epic', 'condition_type': 'completed_bookings', 'condition_value': 20},
            
            # Spending badges
            {'name': 'Dépensier', 'description': 'Total dépensé: 100 TND', 'icon': '💰', 'rarity': 'common', 'condition_type': 'total_spent', 'condition_value': 100},
            {'name': 'Gros Budget', 'description': 'Total dépensé: 500 TND', 'icon': '💎', 'rarity': 'rare', 'condition_type': 'total_spent', 'condition_value': 500},
            {'name': 'Mécène', 'description': 'Total dépensé: 1000 TND', 'icon': '💸', 'rarity': 'epic', 'condition_type': 'total_spent', 'condition_value': 1000},
            
            # Loyalty tier badges
            {'name': 'Bronze Master', 'description': 'Atteindre le niveau Bronze', 'icon': '🥉', 'rarity': 'common', 'condition_type': 'loyalty_tier', 'condition_value': 1},
            {'name': 'Silver Elite', 'description': 'Atteindre le niveau Silver', 'icon': '🥈', 'rarity': 'rare', 'condition_type': 'loyalty_tier', 'condition_value': 2},
            {'name': 'Gold Champion', 'description': 'Atteindre le niveau Gold', 'icon': '🥇', 'rarity': 'epic', 'condition_type': 'loyalty_tier', 'condition_value': 3},
            {'name': 'Platinum Legend', 'description': 'Atteindre le niveau Platinum', 'icon': '💎', 'rarity': 'legendary', 'condition_type': 'loyalty_tier', 'condition_value': 4},
        ]

        created = 0
        for data in badges_data:
            badge, was_created = Badge.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'+ Created: {badge.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'- Already exists: {badge.name}'))

        self.stdout.write(self.style.SUCCESS(f'\nDone! Created {created} new badges.'))
