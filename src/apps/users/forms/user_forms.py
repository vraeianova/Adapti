# Django
from django import forms
from django.contrib.auth import get_user_model

# Django
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import EmailInput, PasswordInput, Select, TextInput

# LOCAL MODELS
from ..models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("email",)


class SignupUsersForm(UserCreationForm):
    # TODO PODER MODIFICAR ESTO EN EL FUTURO
    USER_CHOICES = [
        ("is_employee", "Empleado"),
        ("is_security_guard", "Guardia de seguridad"),
        #    ('is_superuser', 'Administrador'),
    ]

    options = forms.ChoiceField(choices=USER_CHOICES)

    class Meta:
        fields = (
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "options",
        )
        model = get_user_model()
        widgets = {
            "email": EmailInput(attrs={"placeholder": "Correo electrónico"}),
            "first_name": TextInput(attrs={"placeholder": "Nombre"}),
            "last_name": TextInput(attrs={"placeholder": "Apellido"}),
            "password1": PasswordInput(attrs={"placeholder": "Password"}),
            "password2": PasswordInput(attrs={"placeholder": "Confirmación"}),
            "options": Select(attrs={"placeholder": "Seleccione opcion"}),
        }

    def __init__(self, *args, **kwargs):
        super(SignupUsersForm, self).__init__(*args, **kwargs)
        self.error_list = []

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

        self.fields["password1"].required = False
        self.fields["password2"].required = False

        self.fields["password1"].widget = forms.HiddenInput()
        self.fields["password2"].widget = forms.HiddenInput()

    def clean_username(self):
        User = get_user_model()
        username = self.cleaned_data.get("email")

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("¡El usuario ya existe!")

        return username

    def clean_options(self):
        options = self.cleaned_data.get("options")
        if options == "is_employee" or options == "is_superuser":
            return options
        else:
            raise forms.ValidationError("¡No se selecciono opción!")
