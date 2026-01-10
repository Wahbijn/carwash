"""
Django settings for carwash_project project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ============================
# BASE DIR & ENV
# ============================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# ============================
# SECURITY
# ============================
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "False") == "True"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")


# ============================
# INSTALLED APPS
# ============================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # project apps
    "wash",
    "accounts",
    "loyalty",
    "badges",

    # UI helpers
    "crispy_forms",
    "crispy_bootstrap5",

    # Task scheduling
    "django_apscheduler",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# ============================
# MIDDLEWARE
# ============================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================
# URLS & TEMPLATES
# ============================
ROOT_URLCONF = "carwash_project.urls"

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

WSGI_APPLICATION = "carwash_project.wsgi.application"


# ============================
# DATABASE
# ============================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "carwash_db"),
        "USER": os.environ.get("DB_USER", "carwash_user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "motdepassefort"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": int(os.environ.get("DB_PORT", 5432)),
    }
}


# ============================
# PASSWORD VALIDATION
# ============================
AUTH_PASSWORD_VALIDATORS = []


# ============================
# LANGUAGE / TIMEZONE
# ============================
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "Africa/Tunis")
USE_I18N = True
USE_TZ = True


# ============================
# STATIC & MEDIA
# ============================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# ============================
# AUTH REDIRECTS
# ============================
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/accounts/login/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================
# EMAIL — GMAIL SMTP (Final, Stable)
# ============================



EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")              
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")      
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)


# ============================
# OPENAI (optional)
# ============================
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


# ============================
# REMINDER EMAIL SETTINGS
# ============================
# How many hours before a booking to send the reminder email
REMINDER_HOURS_BEFORE = int(os.environ.get("REMINDER_HOURS_BEFORE", 6))

# Logging configuration for scheduler
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'wash.scheduler': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'wash.signals': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
