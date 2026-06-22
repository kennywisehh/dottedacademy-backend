from celery import shared_task
from django.conf import settings
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


def _get_brevo_api():
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY
    return sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))


@shared_task
def send_verification_email_task(first_name, email, token):
    api = _get_brevo_api()
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email}],
        sender={"name": "Dotted Academy", "email": settings.DEFAULT_FROM_EMAIL},
        subject="Verify your Dotted Academy account",
        text_content=f"""Hi {first_name},

Welcome to Dotted Academy! Please verify your email address by using the token below:

Token: {token}

If you did not create an account, please ignore this email.

— The Dotted Academy Team"""
    )
    api.send_transac_email(send_smtp_email)


@shared_task
def send_password_reset_email_task(first_name, email, token):
    api = _get_brevo_api()
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email}],
        sender={"name": "Dotted Academy", "email": settings.DEFAULT_FROM_EMAIL},
        subject="Reset your Dotted Academy password",
        text_content=f"""Hi {first_name},

We received a request to reset your password. Use the token below to reset it:

Token: {token}

If you did not request a password reset, please ignore this email.

— The Dotted Academy Team"""
    )
    api.send_transac_email(send_smtp_email)