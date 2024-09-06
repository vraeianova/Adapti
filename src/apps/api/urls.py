from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views.assistants_views import AssistantCreateView, AssistantSyncView
from .views.conversations_views import HumanInterventionUpdateView
from .views.whatsapp_views import WhatsappWebhook


urlpatterns = [
    path(
        "auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "whatsapp-webhook/", WhatsappWebhook.as_view(), name="whatsapp_webhook"
    ),
    path(
        "assistants/", AssistantCreateView.as_view(), name="assistant-create"
    ),
    path(
        "sync-assistants/", AssistantSyncView.as_view(), name="sync-assistants"
    ),
    # THREADS VIEWS
    path(
        "human-intervention/<str:thread_id>/update/",
        HumanInterventionUpdateView.as_view(),
        name="human-intervention-update",
    ),
]
