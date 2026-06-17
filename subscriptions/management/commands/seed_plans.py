from django.core.management.base import BaseCommand
from subscriptions.models import Plan


class Command(BaseCommand):
    help = 'Seed subscription plans'

    def handle(self, *args, **kwargs):
        plans = [
            {
                'name': 'University Plan',
                'plan_type': 'university',
                'price': 800.00,
                'description': 'Access to all university courses tailored to your department and level.',
            },
            {
                'name': 'Skills Plan',
                'plan_type': 'skills',
                'price': 1500.00,
                'description': 'Access to all skills courses across industries and categories.',
            },
            {
                'name': 'Combined Plan',
                'plan_type': 'combined',
                'price': 2000.00,
                'description': 'Full access to both university and skills courses.',
            },
        ]

        for plan_data in plans:
            plan, created = Plan.objects.get_or_create(
                plan_type=plan_data['plan_type'],
                defaults=plan_data,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created plan: {plan.name}'))
            else:
                self.stdout.write(f'Plan already exists: {plan.name}')