from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_password_reset_email(user_email, reset_url):
    subject = "Восстановление пароля"
    message = f"""
    Для восстановления пароля перейдите по ссылке:
    {reset_url}
    
    Если вы не запрашивали восстановление пароля, проигнорируйте это письмо.
    
    С уважением,
    Команда технической поддержки ООО "Рога и Копыта"
    """
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
