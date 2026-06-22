from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_verification_email_task(first_name, email, token):
    subject = 'Verify your Dotted Academy account'
    message = f'''
Hi {first_name},

Welcome to Dotted Academy! Please verify your email address by using the token below:

Token: {token}

If you did not create an account, please ignore this email.

— The Dotted Academy Team
'''
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


@shared_task
def send_password_reset_email_task(first_name, email, token):
    subject = 'Reset your Dotted Academy password'
    message = f'''
Hi {first_name},

We received a request to reset your password. Use the token below to reset it:

Token: {token}

If you did not request a password reset, please ignore this email.

— The Dotted Academy Team
'''
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])