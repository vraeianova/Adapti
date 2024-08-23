from django.db import models


class OauthToken(models.Model):
    PROVIDER_CHOICES = [
        ("google", "Google"),
        ("zoho", "Zoho"),
    ]

    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES)
    access_token = models.CharField(max_length=512)
    refresh_token = models.CharField(max_length=512)
    token_uri = models.URLField(max_length=1024, null=True, blank=True)
    client_id = models.CharField(max_length=512, null=True, blank=True)
    client_secret = models.CharField(max_length=512, null=True, blank=True)
    scopes = models.TextField(null=True, blank=True)
    universe_domain = models.CharField(max_length=256, null=True, blank=True)
    account = models.CharField(max_length=256, null=True, blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.provider.capitalize()} Token (Expires: {self.expiry or self.token_expiry})"
