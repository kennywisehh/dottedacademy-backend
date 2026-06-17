import uuid
import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import PaymentTransaction, Subscription


def generate_reference():
    return f'DOTTED-{uuid.uuid4().hex[:12].upper()}'


def initiate_paystack(email, amount_naira, reference, callback_url):
    url = 'https://api.paystack.co/transaction/initialize'
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'email': email,
        'amount': int(amount_naira * 100),  # kobo
        'reference': reference,
        'callback_url': callback_url,
    }
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if data.get('status'):
        return {
            'payment_url': data['data']['authorization_url'],
            'reference': reference,
            'gateway': 'paystack',
        }
    raise Exception(data.get('message', 'Paystack initialization failed'))


def initiate_flutterwave(email, amount_naira, reference, callback_url, name):
    url = 'https://api.flutterwave.com/v3/payments'
    headers = {
        'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'tx_ref': reference,
        'amount': str(amount_naira),
        'currency': 'NGN',
        'redirect_url': callback_url,
        'customer': {
            'email': email,
            'name': name,
        },
        'customizations': {
            'title': 'Dotted Academy',
        },
    }
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if data.get('status') == 'success':
        return {
            'payment_url': data['data']['link'],
            'reference': reference,
            'gateway': 'flutterwave',
        }
    raise Exception(data.get('message', 'Flutterwave initialization failed'))


def verify_paystack(reference):
    url = f'https://api.paystack.co/transaction/verify/{reference}'
    headers = {'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
    response = requests.get(url, headers=headers)
    data = response.json()
    if data.get('status') and data['data']['status'] == 'success':
        return True, data['data']
    return False, data


def verify_flutterwave(reference):
    url = f'https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={reference}'
    headers = {'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}'}
    response = requests.get(url, headers=headers)
    data = response.json()
    if data.get('status') == 'success' and data['data']['status'] == 'successful':
        return True, data['data']
    return False, data

def process_payment_reference(reference, gateway):
    try:
        transaction = PaymentTransaction.objects.get(reference=reference)
    except PaymentTransaction.DoesNotExist:
        return False

    if transaction.status == 'success':
        return True  # already processed — idempotent

    if gateway == 'paystack':
        success, gateway_response = verify_paystack(reference)
    else:
        success, gateway_response = verify_flutterwave(reference)

    transaction.gateway_response = gateway_response

    if not success:
        transaction.status = 'failed'
        transaction.save()
        return False

    transaction.status = 'success'
    transaction.save()

    now = timezone.now()
    subscription, created = Subscription.objects.get_or_create(
        user=transaction.user,
        defaults={
            'plan': transaction.plan,
            'status': 'active',
            'current_period_start': now,
            'current_period_end': now + timedelta(days=30),
        }
    )

    if not created:
        subscription.plan = transaction.plan
        subscription.status = 'active'
        subscription.current_period_start = now
        subscription.current_period_end = now + timedelta(days=30)
        subscription.cancelled_at = None
        subscription.save()

    transaction.subscription = subscription
    transaction.save()
    return True