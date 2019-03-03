"""
These settings are specifically from pretalx, refer to pretalx.settings

They are copied in to be editable and co-exist with other Django project
settings.

This module isn't stand-alone but is imported from our settings.dev and
settings.production.
"""
import os

import pretalx

from .base import *  # noqa

INSTALLED_APPS += [
    'bakery',
    'compressor',
    'djangoformsetjs',
    'jquery',
    'rest_framework',
    'rest_framework.authtoken',
    'rules',
    'pretalx.api',
    'pretalx.common',
    'pretalx.event',
    'pretalx.mail',
    'pretalx.person',
    'pretalx.schedule',
    'pretalx.submission',
    'pretalx.agenda',
    'pretalx.cfp',
    'pretalx.orga',
    'bootstrap4',
    'django.forms',
]

# PreTalx users this
LOCAL_APPS = [
    'pretalx.api',
    'pretalx.common',
    'pretalx.event',
    'pretalx.mail',
    'pretalx.person',
    'pretalx.schedule',
    'pretalx.submission',
    'pretalx.agenda',
    'pretalx.cfp',
    'pretalx.orga',
]

# What is this, is it needed?
SITE_URL = 'http://localhost'
SITE_NETLOC = "localhost:8000"


# Unknown where these are used, or if they are specifically for pretalx..
## SECURITY SETTINGS
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

CSP_DEFAULT_SRC = "'self'"
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:")

CSRF_COOKIE_NAME = 'pretalx_csrftoken'

# Needs to be more dynamic
# CSRF_TRUSTED_ORIGINS = [urlparse(SITE_URL).hostname]

SESSION_COOKIE_NAME = 'pretalx_session'
SESSION_COOKIE_HTTPONLY = True


# This is changed if using memcached
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# This is defined in PreTalx, keeping here for now
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

FORMAT_MODULE_PATH = ['pretalx.common.formats']

# Something native to PreTalx?
LANGUAGES_NATURAL_NAMES = [('en', 'English'), ('de', 'Deutsch'), ('fr', 'Français')]
LANGUAGES_OFFICIAL = {'en', 'de'}

# Pretalx wants this..
AUTH_USER_MODEL = 'person.User'
AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
    'pretalx.common.auth.AuthenticationTokenBackend',
)


FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'


for _TEMPLATE in TEMPLATES:
    _TEMPLATE['OPTIONS']['context_processors'] += [
        'pretalx.common.context_processors.add_events',
        'pretalx.common.context_processors.locale_context',
        'pretalx.common.context_processors.messages',
        'pretalx.common.context_processors.system_information',
        'pretalx.orga.context_processors.orga_events',
    ]


# What is this, we need it?
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_DIRS.append(
    os.path.join(os.path.dirname(pretalx.__file__), 'static')
)

BOOTSTRAP4 = {
    'field_renderers': {
        'default': 'bootstrap4.renderers.FieldRenderer',
        'inline': 'bootstrap4.renderers.InlineFieldRenderer',
        'event': 'pretalx.common.forms.renderers.EventFieldRenderer',
        'event-inline': 'pretalx.common.forms.renderers.EventInlineFieldRenderer',
    }
}

# django-bakery / HTML export
# TODO: Figure out the builddir here...
BUILD_DIR = ""
BAKERY_VIEWS = (
    'pretalx.agenda.views.htmlexport.ExportScheduleView',
    'pretalx.agenda.views.htmlexport.ExportFrabXmlView',
    'pretalx.agenda.views.htmlexport.ExportFrabXCalView',
    'pretalx.agenda.views.htmlexport.ExportFrabJsonView',
    'pretalx.agenda.views.htmlexport.ExportICalView',
    'pretalx.agenda.views.htmlexport.ExportScheduleVersionsView',
    'pretalx.agenda.views.htmlexport.ExportTalkView',
    'pretalx.agenda.views.htmlexport.ExportTalkICalView',
    'pretalx.agenda.views.htmlexport.ExportSpeakerView',
)
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ('i18nfield.rest_framework.I18nJSONRenderer',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    # 'DEFAULT_PERMISSION_CLASSES': ('pretalx.api.permissions.ApiPermission',)
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.SearchFilter',
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 25,
    'SEARCH_PARAM': 'q',
    'ORDERING_PARAM': 'o',
    'VERSIONING_PARAM': 'v',
}
