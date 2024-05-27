from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import admin
from django.db import models

from apps.utils.directory_path import user_profile_pic_directory_path


class Profile(models.Model):
    """Profile.
    A profile holds a user's public data like biography, picture,
    and statistics.
    """

    GENDER_CHOICES = (
        (1, "Masculino"),
        (2, "Femenino"),
    )

    id_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    address = models.TextField(db_column="Address", blank=True, null=True)
    phone = models.CharField(
        db_column="Phone", max_length=20, blank=True, null=True
    )
    photo = models.ImageField(
        "profile picture",
        db_column="Photo",
        upload_to=user_profile_pic_directory_path,
        blank=True,
        null=True,
    )
    birth_date = models.DateField(db_column="BirthDate", blank=True, null=True)
    gender = models.IntegerField(choices=GENDER_CHOICES)

    def __str__(self):
        """Return user's str representation."""
        return str(self.id_user)

    @property
    def age(self):
        today = datetime.today()
        age = relativedelta(today, self.birth_date).years
        return age


class ProfileAdmin(admin.ModelAdmin):
    # Definir el método como clave para list_display
    # list_display = ['id_user']

    # Ordenar los perfiles por el campo 'email' del usuario
    ordering = ["id_user__email"]


# Registrando el modelo Profile con el ModelAdmin personalizado
admin.site.register(Profile, ProfileAdmin)
