from django.core.mail import send_mail
from django.utils import timezone

from .models import BulkMailAttempt


def send_bulk_mail(bulk_mail):
    if bulk_mail.status == "Создана":
        bulk_mail.status = "Запущена"
        bulk_mail.sent_at = timezone.now()
        bulk_mail.save(update_fields=["status", "sent_at"])

    all_success = True
    response = ""

    receivers = bulk_mail.receivers.all()
    message = bulk_mail.message

    for receiver in receivers:
        try:
            send_mail(
                subject=message.subject,
                message=message.content,
                from_email="qwarekree@yandex.ru",
                recipient_list=[receiver.email],
                fail_silently=False,
            )
            status = "Успешно"
            response = f"Успешно отправлено: {receiver.email}"
        except Exception as e:
            response = f"Не получилось отправить: {receiver.email} ({e})"
            status = "Не успешно"
        finally:
            BulkMailAttempt.objects.create(
                attempted_at=timezone.now(),
                status=status,
                response=response,
                bulk_mail=bulk_mail,
            )

    return all_success, response
