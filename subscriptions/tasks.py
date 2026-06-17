from celery import shared_task
from django.utils import timezone
from .models import Subscription


@shared_task
def expire_subscriptions():
    now = timezone.now()

    # Expire trials that have ended
    expired_trials = Subscription.objects.filter(
        status='trial',
        trial_end__lte=now,
    )
    expired_trials.update(status='expired')

    # Expire active subscriptions whose period has ended
    expired_active = Subscription.objects.filter(
        status='active',
        current_period_end__lte=now,
    )
    expired_active.update(status='expired')

    return f'Expired {expired_trials.count()} trials and {expired_active.count()} active subscriptions.'