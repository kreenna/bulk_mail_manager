from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from mail.forms import BulkMailForm, MessageForm, ReceiverForm
from mail.models import BulkMail, BulkMailAttempt, Message, Receiver

from .mixins import BlockedUserMixin, OwnerRequiredMixin
from .services import send_bulk_mail


def home_view(request):
    total_bulk_mails = BulkMail.objects.count()
    active_bulk_mails = BulkMail.objects.filter(status="Запущена").count()
    unique_receivers = Receiver.objects.count()

    context = {
        "total_bulk_mails": total_bulk_mails,
        "active_bulk_mails": active_bulk_mails,
        "unique_receivers": unique_receivers,
    }
    return render(request, "mail/home.html", context)


class ReceiverCreateView(LoginRequiredMixin, BlockedUserMixin, CreateView):
    model = Receiver
    form_class = ReceiverForm
    template_name = "mail/receiver_form.html"
    success_url = reverse_lazy("mail:receivers")

    def form_valid(self, form):
        form.instance.owner = self.request.user  # назначаем владельца
        return super().form_valid(form)


class ReceiverListView(LoginRequiredMixin, BlockedUserMixin, ListView):
    model = Receiver
    template_name = "mail/receivers.html"
    context_object_name = "receivers"

    def get_queryset(self):
        if (
            self.request.user.groups.filter(name="managers").exists()
            or self.request.user.is_staff
        ):
            return Receiver.objects.all()
        return Receiver.objects.filter(owner=self.request.user)


class ReceiverDetailView(LoginRequiredMixin, BlockedUserMixin, DetailView):
    model = Receiver
    template_name = "mail/receiver_detail.html"
    context_object_name = "receiver"


class ReceiverUpdateView(
    LoginRequiredMixin, OwnerRequiredMixin, BlockedUserMixin, UpdateView
):
    model = Receiver
    form_class = ReceiverForm
    template_name = "mail/receiver_form.html"

    def get_success_url(self):
        return reverse("mail:receiver_detail", kwargs={"pk": self.object.pk})


@method_decorator(cache_page(60 * 15), name="dispatch")
class ReceiverDeleteView(
    LoginRequiredMixin, OwnerRequiredMixin, BlockedUserMixin, DeleteView
):
    model = Receiver
    template_name = "mail/delete_form.html"
    context_object_name = "receiver"
    success_url = reverse_lazy("mail:receivers")


class MessageCreateView(LoginRequiredMixin, BlockedUserMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mail/message_form.html"
    success_url = reverse_lazy("mail:messages")

    def form_valid(self, form):
        form.instance.owner = self.request.user  # назначаем владельца
        return super().form_valid(form)


class MessageListView(ListView):
    model = Message
    template_name = "mail/messages.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, BlockedUserMixin, DetailView):
    model = Message
    template_name = "mail/message_detail.html"
    context_object_name = "message"


class MessageUpdateView(LoginRequiredMixin, BlockedUserMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mail/message_form.html"

    def get_success_url(self):
        return reverse("mail:message_detail", kwargs={"pk": self.object.pk})


@method_decorator(cache_page(60 * 15), name="dispatch")
class MessageDeleteView(LoginRequiredMixin, BlockedUserMixin, DeleteView):
    model = Message
    template_name = "mail/delete_form.html"
    context_object_name = "message"
    success_url = reverse_lazy("mail:messages")


class BulkMailCreateView(LoginRequiredMixin, BlockedUserMixin, CreateView):
    model = BulkMail
    form_class = BulkMailForm
    template_name = "mail/mail_form.html"
    success_url = reverse_lazy("mail:mails")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user  # назначаем владельца
        return super().form_valid(form)


class ManualSendBulkMailView(View):
    def post(self, request, pk):
        bulk_mail = get_object_or_404(BulkMail, pk=pk)

        all_success, _ = send_bulk_mail(bulk_mail)

        if all_success:
            messages.success(self.request, "Рассылка отправлена успешно.")
        else:
            messages.warning(self.request, "При отправке рассылки возникли ошибки.")

        return redirect("mail:mail_detail", pk=pk)


class BulkMailListView(LoginRequiredMixin, ListView):
    model = BulkMail
    template_name = "mail/mails.html"
    context_object_name = "mails"

    def get_queryset(self):
        if (
            self.request.user.groups.filter(name="managers").exists()
            or self.request.user.is_staff
        ):
            return BulkMail.objects.all()
        return BulkMail.objects.filter(owner=self.request.user)


class BulkMailDetailView(LoginRequiredMixin, DetailView):
    model = BulkMail
    template_name = "mail/mail_detail.html"
    context_object_name = "mail"

    def get_queryset(self):
        queryset = cache.get("bulk_mail_detail_queryset")
        if not queryset:
            queryset = super().get_queryset()
            cache.set(
                "bulk_mail_detail_queryset", queryset, 60 * 15
            )  # кешируем данные на 15 минут
        return queryset


class BulkMailUpdateView(
    LoginRequiredMixin, OwnerRequiredMixin, BlockedUserMixin, UpdateView
):
    model = BulkMail
    form_class = BulkMailForm
    template_name = "mail/mail_form.html"

    def get_success_url(self):
        return reverse("mail:mail_detail", kwargs={"pk": self.object.pk})


class BulkMailStopView(LoginRequiredMixin, View):
    def post(self, request, pk):
        mail = get_object_or_404(BulkMail, id=pk)

        if not request.user.groups.filter(name="managers").exists():
            return HttpResponseForbidden("У вас нет прав для завершения рассылок.")

        mail.status = "Завершена"
        mail.save()

        return redirect("mail:mail_detail", pk)


@method_decorator(cache_page(60 * 15), name="dispatch")
class BulkMailDeleteView(
    LoginRequiredMixin, OwnerRequiredMixin, BlockedUserMixin, DeleteView
):
    model = BulkMail
    template_name = "mail/delete_form.html"
    context_object_name = "mail"
    success_url = reverse_lazy("mail:mails")


class AttemptListView(LoginRequiredMixin, ListView):
    model = BulkMailAttempt
    template_name = "mail/attempts.html"
    context_object_name = "attempts"

    def get_queryset(self):
        if (
            self.request.user.groups.filter(name="managers").exists()
            or self.request.user.is_staff
        ):
            return BulkMailAttempt.objects.all()
        return BulkMailAttempt.objects.filter(bulk_mail__owner=self.request.user)
