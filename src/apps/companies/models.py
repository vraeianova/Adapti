from django.db import models


class Company(models.Model):
    zoho_workspace_id = models.CharField(
        max_length=255, unique=True, blank=True, null=True
    )
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
