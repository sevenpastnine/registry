from .base import * # noqa

DEBUG = True

SITE_ID = 1
# SITE_ID = 2

DJANGO_VITE = {
    'default': {
        'dev_mode': True,
        'static_url_prefix': 'frontend',
    }
}

SECRET_KEY = 'secret-key'

INTERNAL_IPS = ["127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "registry"
    }
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
