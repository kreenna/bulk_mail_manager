from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "first_name", "last_name", "phone_number", "country", "password1", "password2", "avatar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields.keys():  # получаем названия полей

            self.fields[field_name].widget.attrs.update({  # присваиваем значения полям на основании перебора
                "class": "form-control",

            })


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "phone_number", "country", "avatar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields.keys():  # получаем названия полей

            self.fields[field_name].widget.attrs.update({  # присваиваем значения полям на основании перебора
                "class": "form-control",

            })
