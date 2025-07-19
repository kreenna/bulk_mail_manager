from django import forms

from .models import BulkMail, Message, Receiver


class ReceiverForm(forms.ModelForm):
    class Meta:
        model = Receiver
        fields = ["email", "full_name", "comment"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields.keys():  # получаем названия полей

            self.fields[field_name].widget.attrs.update(
                {  # присваиваем значения полям на основании перебора
                    "class": "form-control",
                }
            )


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["subject", "content"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields.keys():  # получаем названия полей

            self.fields[field_name].widget.attrs.update(
                {  # присваиваем значения полям на основании перебора
                    "class": "form-control",
                }
            )


class BulkMailForm(forms.ModelForm):
    class Meta:
        model = BulkMail
        fields = ["name", "message", "receivers", "status"]
        widgets = {
            "receivers": forms.SelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            # Assuming Message and Receiver have a ForeignKey 'owner' to the User model
            self.fields["message"].queryset = Message.objects.filter(owner=user)
            self.fields["receivers"].queryset = Receiver.objects.filter(owner=user)

        for field_name in self.fields.keys():  # получаем названия полей
            self.fields[field_name].widget.attrs.update(
                {  # присваиваем значения полям на основании перебора
                    "class": "form-control",
                }
            )
