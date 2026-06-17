import os
from celery import Celery
from celery.schedules import crontab
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'expire-subscriptions-daily': {
        'task': 'subscriptions.tasks.expire_subscriptions',
        'schedule': crontab(hour=0, minute=0),  # runs every midnight
    },
}