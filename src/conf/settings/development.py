import os
from datetime import timedelta

from dotenv import load_dotenv

from .base import BASE_DIR, INSTALLED_APPS, MIDDLEWARE, TEMPLATES


load_dotenv()


def show_toolbar(request):
    return False


# =================DEBUG=================
DEBUG = os.getenv("DEBUG", "False") == "True"
SECRET_KEY = os.getenv("SECRET_KEY")

# =================DATABASE=================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        "ATOMIC_REQUESTS": True,
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =================SECURITY=================
ALLOWED_HOSTS = [
    "localhost",
    "0.0.0.0",
    "127.0.0.1",
]

# =================TEMPLATES=================
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG  # NOQA

# =================CACHES=================
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}


# =================APPS=================
INSTALLED_APPS += ["django_extensions", "debug_toolbar", "gunicorn"]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.history.HistoryPanel",
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.logging.LoggingPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
]

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

# REST FRAMEWORK
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}

# JWT CONFIGURATION
JWT_AUTH = {
    "JWT_SECRET_KEY": SECRET_KEY,
    "JWT_ALGORITHM": "HS256",
    "JWT_ALLOW_REFRESH": True,
    "JWT_EXPIRATION_DELTA": timedelta(days=30),
    # "JWT_REFRESH_EXPIRATION_DELTA": timedelta(minutes=10),
}
