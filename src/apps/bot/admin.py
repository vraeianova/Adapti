from django.contrib import admin

from .models import OauthToken


@admin.register(OauthToken)
class OauthTokenAdmin(admin.ModelAdmin):
    list_display = ("access_token", "refresh_token", "token_expiry")
