from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from .settings.base import MEDIA_ROOT, MEDIA_URL, STATIC_ROOT, STATIC_URL


schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def trigger_error(request):
    division_by_zero = 1 / 0
    return division_by_zero


urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("api/v1/", include("apps.api.urls")),
        path("api/v1/services/", include("apps.services.urls")),
        path(
            "api/v1/docs<format>/",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
        path(
            "api/v1/docs/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path(
            "api/v1/redoc/",
            schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc",
        ),
        path("sentry-debug/", trigger_error),
    ]
    + static(STATIC_URL, document_root=STATIC_ROOT)
    + static(MEDIA_URL, document_root=MEDIA_ROOT)
)


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

# Error Handling
handler500 = "apps.utils.handler500"
handler404 = "apps.utils.handler404"
