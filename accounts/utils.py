from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(user, token):
    subject = 'Verify your Dotted Academy account'
    message = f'''
Hi {user.first_name},

Welcome to Dotted Academy! Please verify your email address by using the token below:

Token: {token}

If you did not create an account, please ignore this email.

— The Dotted Academy Team
'''
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_password_reset_email(user, token):
    subject = 'Reset your Dotted Academy password'
    message = f'''
Hi {user.first_name},

We received a request to reset your password. Use the token below to reset it:

Token: {token}

If you did not request a password reset, please ignore this email.

— The Dotted Academy Team
'''
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])