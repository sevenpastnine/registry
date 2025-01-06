import os
from .base import * # noqa
from .base import BASE_DIR

DEBUG = False

DJANGO_VITE = {
    'default': {
        'dev_mode': False,
        'static_url_prefix': 'frontend',
        'manifest_path': BASE_DIR / '../var/static/frontend/manifest.json'
    }
}

ADMINS = (
    ('Joh Dokler', 'joh.dokler@sevenpastnine.com'),
    ('Maja Brajnik', 'maja.brajnik@sevenpastnine.com'),
)

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = [host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")]

SERVER_EMAIL = os.getenv("SERVER_EMAIL")

EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"

ANYMAIL = {
    "MAILGUN_API_URL": os.getenv("MAILGUN_API_URL"),
    "MAILGUN_API_KEY": os.getenv("MAILGUN_API_KEY"),
    "MAILGUN_SENDER_DOMAIN": os.getenv("MAILGUN_SENDER_DOMAIN"),
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("POSTGRES_HOST"),
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
    }
}

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

USE_ETAGS = True