from django.db import models


class ZohoToken(models.Model):
    access_token = models.CharField(max_length=512)
    refresh_token = models.CharField(max_length=512)
    token_expiry = models.DateTimeField()

    def __str__(self):
        return f"ZohoToken (Expires: {self.token_expiry})"
