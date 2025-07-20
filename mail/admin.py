from django.contrib import admin

from .models import BulkMail, BulkMailAttempt, Message, Receiver


@admin.register(Receiver)
class ReceiverAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name")
    search_fields = ("full_name",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "subject")
    search_fields = ("subject",)


@admin.register(BulkMail)
class BulkMailAdmin(admin.ModelAdmin):
    list_display = ("id", "finished_at", "status", "message")
    list_filter = ("status",)
    search_fields = ("message", "receivers")

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == "messages":
                kwargs["queryset"] = Message.objects.filter(owner=request.user)
            if db_field.name == "receivers":
                kwargs["queryset"] = Receiver.objects.filter(owner=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(BulkMailAttempt)
class BulkMailAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "attempted_at", "status", "response", "bulk_mail")
    list_filter = ("status",)
    search_fields = ("bulk_mail",)
