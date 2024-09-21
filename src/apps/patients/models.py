from django.contrib import admin
from django.db import models


class Patient(models.Model):
    name = models.CharField(
        db_column="Name", max_length=100, blank=True, null=True
    )
    email = models.EmailField("Email", blank=True, null=True, max_length=254)
    phone_number = models.CharField(
        db_column="PhoneNumber", max_length=15, blank=True, null=True
    )
    address = models.TextField(db_column="Address", blank=True, null=True)

    class Meta:
        db_table = "Patient"

    def __str__(self):
        return self.name


admin.site.register(Patient)
