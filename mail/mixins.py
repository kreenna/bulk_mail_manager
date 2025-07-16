from django.contrib.auth import logout
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user or self.request.user.is_staff


class BlockedUserMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, "is_blocked", True):
            logout(request)
            return render(request, "users/blocked.html")
        return super().dispatch(request, *args, **kwargs)
