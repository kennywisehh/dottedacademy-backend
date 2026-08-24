import logging
from celery import shared_task
from django.conf import settings
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

logger = logging.getLogger(__name__)


def _get_brevo_api():
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY
    return sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))


def send_verification_email_task(first_name, email, token):
    api = _get_brevo_api()
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email}],
        sender={"name": "Dotted Academy", "email": settings.DEFAULT_FROM_EMAIL},
        subject="Verify your Dotted Academy account",
        text_content=f"""Hi {first_name},

Welcome to Dotted Academy! Please verify your email address by using the code below:

Code: {token}

This code expires in 15 minutes.

If you did not create an account, please ignore this email.

— The Dotted Academy Team"""
    )
    try:
        api.send_transac_email(send_smtp_email)
    except ApiException as e:
        logger.error(f"Failed to send verification email to {email}: {e}")
        raise


def send_password_reset_email_task(first_name, email, token):
    api = _get_brevo_api()
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email}],
        sender={"name": "Dotted Academy", "email": settings.DEFAULT_FROM_EMAIL},
        subject="Reset your Dotted Academy password",
        text_content=f"""Hi {first_name},

We received a request to reset your password. Use the code below to reset it:

Code: {token}

This code expires in 15 minutes.

If you did not request a password reset, please ignore this email.

— The Dotted Academy Team"""
    )
    try:
        api.send_transac_email(send_smtp_email)
    except ApiException as e:
        logger.error(f"Failed to send password reset email to {email}: {e}")
        raise