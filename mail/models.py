from django.conf import settings
from django.db import models


class Receiver(models.Model):
    email = models.EmailField(unique=True, verbose_name="Почта")
    full_name = models.CharField(max_length=250, unique=True, verbose_name="ФИО")
    comment = models.TextField(verbose_name="Комментарий", null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="Получатели"
    )

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"

    def __str__(self):
        return self.email


class Message(models.Model):
    subject = models.CharField(max_length=250, verbose_name="Тема письма")
    content = models.TextField(verbose_name="Содержание")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages"
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class BulkMail(models.Model):
    STATUS_CHOICES = [
        ("Завершена", "Завершена"),
        ("Создана", "Создана"),
        ("Запущена", "Запущена"),
    ]

    name = models.CharField(
        max_length=250, unique=True, verbose_name="Название рассылки"
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="Создана", verbose_name="Статус"
    )
    message = models.ForeignKey(
        Message, verbose_name="Сообщение", on_delete=models.CASCADE
    )
    receivers = models.ManyToManyField(Receiver)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bulk_mails"
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = (("can_disable_mail", "Can disable mail"),)


class BulkMailAttempt(models.Model):
    STATUS_CHOICES = [("Успешно", "Успешно"), ("Не успешно", "Не успешно")]

    attempted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="successful",
        verbose_name="Статус",
    )
    response = models.TextField()
    bulk_mail = models.ForeignKey(
        BulkMail, on_delete=models.CASCADE, related_name="attempts"
    )

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
