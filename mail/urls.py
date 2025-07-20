from django.urls import path

from mail.apps import MailConfig
from mail.views import (
    AttemptListView,
    BulkMailCreateView,
    BulkMailDeleteView,
    BulkMailDetailView,
    BulkMailListView,
    BulkMailStopView,
    BulkMailUpdateView,
    ManualSendBulkMailView,
    MessageCreateView,
    MessageDeleteView,
    MessageDetailView,
    MessageListView,
    MessageUpdateView,
    ReceiverCreateView,
    ReceiverDeleteView,
    ReceiverDetailView,
    ReceiverListView,
    ReceiverUpdateView,
    home_view,
)

app_name = MailConfig.name

urlpatterns = [
    path("", home_view, name="home"),
    path("mail/receiver/create/", ReceiverCreateView.as_view(), name="receiver_create"),
    path(
        "mail/receiver/detail/<int:pk>/",
        ReceiverDetailView.as_view(),
        name="receiver_detail",
    ),
    path("mail/receivers/", ReceiverListView.as_view(), name="receivers"),
    path(
        "mail/receiver/edit/<int:pk>/",
        ReceiverUpdateView.as_view(),
        name="receiver_edit",
    ),
    path(
        "mail/receiver/delete/<int:pk>/",
        ReceiverDeleteView.as_view(),
        name="receiver_delete",
    ),
    path("mail/message/create/", MessageCreateView.as_view(), name="message_create"),
    path(
        "mail/message/detail/<int:pk>/",
        MessageDetailView.as_view(),
        name="message_detail",
    ),
    path("mail/messages/", MessageListView.as_view(), name="messages"),
    path(
        "mail/message/edit/<int:pk>/", MessageUpdateView.as_view(), name="message_edit"
    ),
    path(
        "mail/message/delete/<int:pk>/",
        MessageDeleteView.as_view(),
        name="message_delete",
    ),
    path("mail/mail/create/", BulkMailCreateView.as_view(), name="mail_create"),
    path(
        "mail/mail/detail/<int:pk>/", BulkMailDetailView.as_view(), name="mail_detail"
    ),
    path("mail/mails/", BulkMailListView.as_view(), name="mails"),
    path("mail/edit/<int:pk>/", BulkMailUpdateView.as_view(), name="mail_edit"),
    path("mail/delete/<int:pk>/", BulkMailDeleteView.as_view(), name="mail_delete"),
    path("mail/stop/<int:pk>/", BulkMailStopView.as_view(), name="mail_stop"),
    path("mail/attempts/", AttemptListView.as_view(), name="attempts"),
    path("mail/<int:pk>/send/", ManualSendBulkMailView.as_view(), name="mail_send"),
]
