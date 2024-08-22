from django.urls import path

from apps.bot.services.communication_channels_services.whatsapp_service import (
    WhatsAppService,
)
from apps.bot.views import OAuth2CallbackView


urlpatterns = [
    path(
        "whatsapp-webhook/", WhatsAppService.as_view(), name="whatsapp-webhook"
    ),
    path(
        "oauth2callback/",
        OAuth2CallbackView.as_view(),
        name="oauth2callback",
    ),
]
