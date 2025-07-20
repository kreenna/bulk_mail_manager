from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from mail.models import BulkMailAttempt
from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser


class RegisterView(CreateView):
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        self.send_welcome_email(user.email)
        self.send_activation_email(self.request, user)
        return super().form_valid(form)

    @staticmethod
    def send_welcome_email(user_email):
        subject = "Добро пожаловать в наш сервис"
        message = """Спасибо, что зарегистрировались в нашем сервисе! 
        Мы также отправили вам код для активации аккаунта в другом письме, проверьте ваши входящие сообщения!"""
        from_email = "qwarekree@yandex.ru"
        recipient_list = [user_email]
        send_mail(subject, message, from_email, recipient_list)

    @staticmethod
    def send_activation_email(request, user):
        current_site = get_current_site(request)
        mail_subject = "Активация аккаунта"
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        from_email = "qwarekree@yandex.ru"
        protocol = "https" if request.is_secure() else "http"
        message = render_to_string(
            "users/activation_email.txt",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": uid,
                "token": token,
                "protocol": protocol,
            },
        )
        email = EmailMessage(mail_subject, message, from_email, to=[user.email])
        email.send()


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect("users:login")
    else:
        return render(request, "activation_invalid.html")


class UsersListView(ListView):
    model = CustomUser
    template_name = "users/users_list.html"
    context_object_name = "users"

    def get_queryset(self):
        if self.request.user.groups.filter(name="managers").exists():
            return [user for user in CustomUser.objects.filter(is_staff=False) if user.id != self.request.user.id]
        elif self.request.user.is_superuser:
            return CustomUser.objects.all()
        else:
            return HttpResponseForbidden("У вас нет прав для просмотра пользователей.")


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "users/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_to_view = self.object
        context["user_to_view"] = user_to_view
        context["total_bulk_mails"] = user_to_view.bulk_mails.count()
        context["attempts_success"] = BulkMailAttempt.objects.filter(
            bulk_mail__owner=user_to_view, status="Успешно"
        ).count()
        context["attempts_fail"] = BulkMailAttempt.objects.filter(
            bulk_mail__owner=user_to_view, status="Не успешно"
        ).count()
        return context


@method_decorator(cache_page(60 * 15), name="dispatch")
class ProfileUpdateView(UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = "users/register.html"

    def get_success_url(self):
        return reverse("users:profile", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        return super().form_valid(form)


@method_decorator(cache_page(60 * 15), name="dispatch")
class ProfileDeleteView(DeleteView):
    model = CustomUser
    template_name = "users/profile_delete.html"
    success_url = reverse_lazy("mail:home")


class CustomPasswordChangeView(auth_views.PasswordChangeView):
    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:password_change_done")


class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = "users/password_reset_form.html"
    success_url = reverse_lazy("users:password_reset_done")


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)


email_verification_token = EmailVerificationTokenGenerator()


class BlockUserView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(CustomUser, id=pk)

        if not request.user.has_perm("users.can_block_user"):
            return HttpResponseForbidden("У вас нет прав для блокировки пользователей.")

        user.is_banned = True
        user.save()

        return redirect("mail:home")
