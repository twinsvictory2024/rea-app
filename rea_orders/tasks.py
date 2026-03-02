from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


@shared_task
def send_customer_new_order_email(order_id, customer_email):
    """
    Отправка уведомления покупателю о подтверждении заказа
    """
    subject = "✅ Ваш заказ подтвержден"
    
    message = f"""
    Здравствуйте!
    
    Ваш заказ №{order_id[:8]} успешно подтвержден и принят в обработку.
    
    Наши роботы-гуманоиды уже занимаются упаковкой Вашего заказа.
    Статус заказа вы можете отслеживать в личном кабинете.
    
    Детали заказа: {settings.FRONTEND_URL}/orders/{order_id}
    
    С уважением,
    Команда ООО "Рога и Копыта"
    """
    
    html_message = f"""
    <h2>Здравствуйте!</h2>
    
    <p>Ваш заказ №<strong>{order_id[:8]}</strong> успешно подтвержден и принят в обработку.</p>
    
    <p>Наши роботы-гуманоиды уже занимаются упаковкой Вашего заказа.<br>
    Статус заказа вы можете отслеживать в личном кабинете.</p>
    
    <p><a href="{settings.FRONTEND_URL}/orders/{order_id}" 
          style="background-color: #4CAF50; color: white; padding: 10px 20px; 
                 text-decoration: none; border-radius: 5px;">
        Отследить заказ
    </a></p>
    
    <p>С уважением,<br>Команда ООО "Рога и Копыта"</p>
    """
    
    send_mail(
        subject=subject,
        message=message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[customer_email],
        fail_silently=False,
    )


@shared_task
def send_vendor_new_order_email(vendor_email, order_id):
    """
    Отправка уведомления продавцу о новом заказе
    """
    subject = "📦 Новый заказ ожидает обработки"
    
    message = f"""
    Уважаемый поставщик!
    
    Получен новый заказ №{order_id[:8]}, содержащий ваши товары.
    
    Пожалуйста, попросите ваших роботов-гуманоидов поскорее упаковать товары.
    Статус заказа необходимо обновлять в личном кабинете.
    
    Детали заказа: {settings.FRONTEND_URL}/vendor/orders/{order_id}
    
    С уважением,
    Отдел по работе с клиентами ООО "Рога и Копыта"
    """
    
    html_message = f"""
    <h2>Уважаемый поставщик!</h2>
    
    <p>Получен новый заказ №<strong>{order_id[:8]}</strong>, содержащий ваши товары.</p>
    
    <p>Пожалуйста, попросите ваших роботов-гуманоидов поскорее упаковать товары.<br>
    Статус заказа необходимо обновлять в личном кабинете.</p>
    
    <p><a href="{settings.FRONTEND_URL}/vendor/orders/{order_id}" 
          style="background-color: #2196F3; color: white; padding: 10px 20px; 
                 text-decoration: none; border-radius: 5px;">
        Перейти к заказу
    </a></p>
    
    <p>С уважением,<br>Команда ООО "Рога и Копыта"</p>
    """
    
    send_mail(
        subject=subject,
        message=message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[vendor_email],
        fail_silently=False,
    )