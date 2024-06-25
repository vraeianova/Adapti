"""Base settings to build other settings files upon."""

import os
from pathlib import Path

import environ
from dotenv import load_dotenv


load_dotenv()
environ.Env.read_env()
# =================DIRS=================
ROOT_DIR = environ.Path(__file__) - 3
APPS_DIR = ROOT_DIR.path("apps")
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# ===========ENVIRONMENT=====================
DEBUG = os.getenv("DEBUG")

# =================LANGUAGE AND TIMEZONE=================
LANGUAGE_CODE = "en-us"
SITE_ID = 1
TIME_ZONE = "America/Tegucigalpa"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# =================URL CONF=================
ROOT_URLCONF = os.getenv("ROOT_URLCONF")

# =================WSGI=================
WSGI_APPLICATION = "conf.wsgi.application"

# =================AUTH USER MODEL=================
AUTH_USER_MODEL = "users.CustomUser"

# =================APPS=================
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "import_export",
    "rest_framework",
    "drf_yasg",
]

LOCAL_APPS = [
    "apps.users",
    "apps.utils",
    "apps.api",
    "apps.bot",
]


INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
# =================PASSWORD_HASHERS=================
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# =================MIDDLEWARE=================
DJANGO_MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

MIDDLEWARE = DJANGO_MIDDLEWARE

# =================STATIC FILES=================
STATIC_ROOT = str(ROOT_DIR("staticfiles"))
STATIC_ROOT = os.path.join(ROOT_DIR, "staticfiles")

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    str(ROOT_DIR.path("static")),
]

# print("testing static root", STATIC_ROOT)

# STATICFILES_FINDERS = [
#     "django.contrib.staticfiles.finders.FileSystemFinder",
#     "django.contrib.staticfiles.finders.AppDirectoriesFinder",
# ]

# =================MEDIA=================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =================TEMPLATES=================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# =================SECURITY=================
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 60 * 60 * 24
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# =================ADMIN=================
ADMIN_URL = "admin/"
ADMINS = [("Cristopher Arias", "vraeianova@gmail.com")]
