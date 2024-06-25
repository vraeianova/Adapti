from django.urls import path

from apps.bot.services.communication_channels_services.whatsapp_service import (
    WhatsAppService,
)


urlpatterns = [
    path(
        "whatsapp-webhook/", WhatsAppService.as_view(), name="whatsapp-webhook"
    ),
]
