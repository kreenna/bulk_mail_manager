from django.core.mail import send_mail
from django.utils import timezone

from .models import BulkMailAttempt


def send_bulk_mail(bulk_mail):
    receivers = bulk_mail.receivers
    message = bulk_mail.message

    try:
        response = send_mail(subject=message.subject, message=message.content, from_email="qwarekree@yandex.ru",
                             recipient_list=receivers, fail_silently=False)
        status = "Успешно"
    except Exception as e:
        response = str(e)
        status = "Не успешно"
    BulkMailAttempt.objects.create(
        attempted_at=timezone.now(),
        status=status,
        server_response=response,
        bulk_mail=bulk_mail
    )
