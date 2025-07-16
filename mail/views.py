from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import DetailView, CreateView, ListView, UpdateView, DeleteView

from mail.forms import MessageForm, ReceiverForm, BulkMailForm
from mail.models import Receiver, Message, BulkMail, BulkMailAttempt
from .mixins import OwnerRequiredMixin, BlockedUserMixin
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
        if self.request.user.groups.filter(name="managers").exists() or self.request.user.is_staff:
            return Receiver.objects.all()
        return Receiver.objects.filter(owner=self.request.user)


class ReceiverDetailView(LoginRequiredMixin, BlockedUserMixin, DetailView):
    model = Receiver
    template_name = "mail/receiver_detail.html"
    context_object_name = "receiver"


class ReceiverUpdateView(LoginRequiredMixin, OwnerRequiredMixin, BlockedUserMixin, UpdateView):
    model = Receiver
    form_class = ReceiverForm
    template_name = "mail/receiver_form.html"

    def get_success_url(self):
        return reverse("mail:receiver_detail", kwargs={"pk": self.object.pk})


class ReceiverDeleteView(LoginRequiredMixin, OwnerRequiredMixin, BlockedUserMixin, DeleteView):
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

    def form_valid(self, form):
        form.instance.owner = self.request.user  # назначаем владельца
        response = super().form_valid(form)
        all_success, _ = send_bulk_mail(self.object)

        if all_success:
            messages.success(self.request, "Рассылка создана и отправлена успешно.")
        else:
            messages.warning(self.request, "Рассылка создана, однако при отправке возникли ошибки.")

        return response


class BulkMailListView(LoginRequiredMixin, ListView):
    model = BulkMail
    template_name = "mail/mails.html"
    context_object_name = "mails"

    def get_queryset(self):
        if self.request.user.groups.filter(name="managers").exists() or self.request.user.is_staff:
            return BulkMail.objects.all()
        return BulkMail.objects.filter(owner=self.request.user)


class BulkMailDetailView(LoginRequiredMixin, DetailView):
    model = BulkMail
    template_name = "mail/mail_detail.html"
    context_object_name = "mail"


class BulkMailUpdateView(LoginRequiredMixin, OwnerRequiredMixin, BlockedUserMixin, UpdateView):
    model = BulkMail
    form_class = BulkMailForm
    template_name = "mail/mail_form.html"

    def get_success_url(self):
        return reverse("mail:mail_detail", kwargs={"pk": self.object.pk})


class BulkMailStopView(LoginRequiredMixin, View):
    def post(self, request, mail_id):
        mail = get_object_or_404(BulkMail, id=mail_id)

        if not request.user.groups.filter(name="Менеджеры").exists():
            return HttpResponseForbidden("У вас нет прав для завершения рассылок.")

        mail.status = "Завершена"
        mail.save()

        return redirect("mail:mails")


class BulkMailDeleteView(LoginRequiredMixin, OwnerRequiredMixin, BlockedUserMixin, DeleteView):
    model = BulkMail
    template_name = "mail/delete_form.html"
    context_object_name = "mail"
    success_url = reverse_lazy("mail:mails")


class ManualSendBulkMailView(View):
    def post(self, request, pk):
        bulk_mail = get_object_or_404(BulkMail, pk=pk)
        send_bulk_mail(bulk_mail)
        messages.success(request, "Рассылка отправлена (попытка зафиксирована)")
        return redirect("mail:mail_detail", pk=pk)


class AttemptListView(LoginRequiredMixin, ListView):
    model = BulkMailAttempt
    template_name = "mail/attempts.html"
    context_object_name = "attempts"

    def get_queryset(self):
        if self.request.user.groups.filter(name="managers").exists() or self.request.user.is_staff:
            return BulkMailAttempt.objects.all()
        return BulkMailAttempt.objects.filter(attempts__owner=self.request.user)