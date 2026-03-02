from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.conf import settings
from .tasks import send_password_reset_email


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    frontend_url = getattr(settings, 'FRONTEND_URL')
    reset_url = f"{frontend_url}/auth/password-reset-confirm/?password_reset_token={reset_password_token.key}"
    
    send_password_reset_email.delay(
        user_email=reset_password_token.user.email,
        reset_url=reset_url
    )