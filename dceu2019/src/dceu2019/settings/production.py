from .base import *  # noqa
from .pretalx import *  # noqa

MANAGERS = ADMINS = [
    ("Main admin team", "info@django-denmark.org")
]

MAIL_FROM = SERVER_EMAIL = DEFAULT_FROM_EMAIL = "content@djangocon.eu"

# For email, you wanna put something like this in production env's
# settings.local:
"""
EMAIL_HOST = config.get('mail', 'host')
EMAIL_PORT = config.get('mail', 'port')
EMAIL_HOST_USER = config.get('mail', 'user')
EMAIL_HOST_PASSWORD = config.get('mail', 'password')
EMAIL_USE_TLS = config.getboolean('mail', 'tls')
EMAIL_USE_SSL = config.getboolean('mail', 'ssl')
"""

# TODO: Need to figure out if this goes in settings.local
CELERY_BROKER_URL = ""
CELERY_RESULT_BACKEND = ""

# There is only one entry... but whatevs :)
for _TEMPLATE in TEMPLATES:
    _TEMPLATE['OPTIONS'].setdefault('loaders', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]
    )
    _TEMPLATE['OPTIONS']['loaders'].insert(0, 'django.template.loaders.cached.Loader')

COMPRESS_ENABLED = COMPRESS_OFFLINE = not DEBUG
