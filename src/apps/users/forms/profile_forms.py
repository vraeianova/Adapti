# Django
from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from apps.users.models.profiles import Profile


class ProfileCreateForm(ModelForm):
    class Meta:
        model = Profile
        fields = (
            "phone",
            "birth_date",
            "gender",
            "address",
        )

        labels = {
            "phone": "Teléfono",
            "birth_date": "Fecha de nacimiento",
            "gender": "Género",
            "address": "Dirección",
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(ProfileCreateForm, self).__init__(*args, **kwargs)
        self.error_list = []

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

        self.fields["phone"].required = True
        self.fields["birth_date"].required = True
        self.fields["gender"].required = True
        self.fields["address"].required = True

        for fieldname in ["gender"]:
            self.fields[fieldname].widget.attrs["class"] = "chosen-select"

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get("birth_date")
        now = datetime.now()

        if not birth_date or birth_date > now.date():
            self.error_list.append("¡Ingresa una fecha de nacimiento válida!")
            raise forms.ValidationError(
                "¡Ingresa una fecha de nacimiento válida!"
            )

        try:
            datetime.strptime(str(birth_date), "%Y-%m-%d")
        except ValueError:
            self.error_list.append(
                "¡El formato de la fecha debe ser yyyy-mm-dd!"
            )
            raise forms.ValidationError(
                "¡El formato de la fecha debe ser yyyy-mm-dd!"
            )

        return birth_date

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone.isdigit():
            self.error_list.append(
                "¡El número de teléfono debe contener solo dígitos!"
            )
            raise ValidationError(
                "¡El número de teléfono debe contener solo dígitos!"
            )
        return phone
