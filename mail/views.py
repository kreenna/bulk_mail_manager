from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView, CreateView, ListView, UpdateView, DeleteView

from mail.forms import MessageForm, ReceiverForm, BulkMailForm
from mail.models import Receiver, Message, BulkMail


def home_view(request):
    return render(request, "mail/home.html")


class ReceiverCreateView(LoginRequiredMixin, CreateView):
    model = Receiver
    form_class = ReceiverForm
    template_name = "mail/receiver_form.html"
    success_url = reverse_lazy("mail:messages")


class ReceiverListView(ListView):
    model = Receiver
    template_name = "mail/receivers.html"
    context_object_name = "receivers"


class ReceiverDetailView(LoginRequiredMixin, DetailView):
    model = Receiver
    template_name = "mail/receiver_detail.html"
    context_object_name = "receiver"


class ReceiverUpdateView(LoginRequiredMixin, UpdateView):
    model = Receiver
    form_class = ReceiverForm
    template_name = "mail/receiver_form.html"

    def get_success_url(self):
        return reverse("mail:receiver_detail", kwargs={"pk": self.object.pk})


class ReceiverDeleteView(LoginRequiredMixin, DeleteView):
    model = Receiver
    template_name = "mail/delete_form.html"
    context_object_name = "receiver"
    success_url = reverse_lazy("mail:receivers")


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mail/message_form.html"
    success_url = reverse_lazy("mail:messages")


class MessageListView(ListView):
    model = Message
    template_name = "mail/messages.html"
    context_object_name = "messages"


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "mail/message_detail.html"
    context_object_name = "message"


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mail/message_form.html"

    def get_success_url(self):
        return reverse("mail:message_detail", kwargs={"pk": self.object.pk})


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mail/delete_form.html"
    context_object_name = "message"
    success_url = reverse_lazy("mail:messages")


class BulkMailCreateView(LoginRequiredMixin, CreateView):
    model = BulkMail
    form_class = BulkMailForm
    template_name = "mail/mail_form.html"
    success_url = reverse_lazy("mail:mails")


class BulkMailListView(ListView):
    model = BulkMail
    template_name = "mail/mails.html"
    context_object_name = "mails"


class BulkMailDetailView(LoginRequiredMixin, DetailView):
    model = BulkMail
    template_name = "mail/mail_detail.html"
    context_object_name = "mail"


class BulkMailUpdateView(LoginRequiredMixin, UpdateView):
    model = BulkMail
    form_class = BulkMailForm
    template_name = "mail/mail_form.html"

    def get_success_url(self):
        return reverse("mail:mail_detail", kwargs={"pk": self.object.pk})


class BulkMailDeleteView(LoginRequiredMixin, DeleteView):
    model = BulkMail
    template_name = "mail/delete_form.html"
    context_object_name = "mail"
    success_url = reverse_lazy("mail:mails")
