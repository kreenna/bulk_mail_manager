from django.contrib.auth import get_user_model
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth import views as auth_views
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.conf import settings

from .forms import CustomUserCreationForm, CustomUserChangeForm
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
        message = render_to_string("users/activation_email.txt", {
            "user": user,
            "domain": current_site.domain,
            "uid": uid,
            "token": token,
            "protocol": protocol,
        })
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


class ProfileDetailView(DetailView):
    model = CustomUser
    template_name = "users/profile.html"


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
