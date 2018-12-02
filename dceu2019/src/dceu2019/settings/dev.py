from .base import *  # noqa
from .pretalx import *  # noqa

DEBUG = True

# IP addresses marked as “internal” that can use the debug_toolbar
# https://docs.djangoproject.com/en/2.0/ref/settings/#internal-ips
INTERNAL_IPS = ["localhost", "127.0.0.1", "[::1]"]

# List of strings representing the host/domain names that this site can serve
# https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

INSTALLED_APPS += ("debug_toolbar",)

MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CELERY_TASK_ALWAYS_EAGER = True

DEBUG_TOOLBAR_PATCH_SETTINGS = False
DEBUG_TOOLBAR_CONFIG = {'JQUERY_URL': ''}

COMPRESS_ENABLED = False

# Some stuff from PreTalx
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] += (
    'rest_framework.renderers.BrowsableAPIRenderer',
)
REST_FRAMEWORK['COMPACT_JSON'] = False
