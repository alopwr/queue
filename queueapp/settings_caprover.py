from .settings import config

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

ALLOWED_HOSTS = config("CR_HOSTS").split(",")
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_REFERRER_POLICY = "same-origin"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [config("CR_REDIS_HOST", "redis://localhost:6379")],
            "password": config("CR_REDIS_PASSWORD"),
        },
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("CR_DB_NAME"),
        "USER": config("CR_DB_USER"),
        "PASSWORD": config("CR_DB_PASSWORD"),
        "HOST": config("CR_DB_HOST"),
        "PORT": config("CR_DB_PORT"),
    }
}


sentry_sdk.init(
    dsn=config("SENTRY_DSN"),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)
