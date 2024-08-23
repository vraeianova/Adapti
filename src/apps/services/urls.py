from django.urls import path

from apps.services.views import WhatsAppService


urlpatterns = [
    path(
        "whatsapp-webhook/", WhatsAppService.as_view(), name="whatsapp-webhook"
    ),
]
