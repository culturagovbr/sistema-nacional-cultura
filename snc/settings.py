# -*- coding: utf-8 -*-
"""
Django settings for snc project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
# from __future__ import absolute_import, unicode_literals
from django.contrib.messages import constants as messages

import environ

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


env = environ.Env(
    DEBUG=(bool, False),
    SENTRY_DSN=(str, None),
    )

env.read_env()

ROOT_DIR = environ.Path(__file__) - 2  # (/a/b/myfile.py - 3 = /)

RECEIVER_EMAIL = env("RECEIVER_EMAIL", default="none@email.com")
# DEBUG
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env("DEBUG", default=False)

# SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY", default='CHANGEME!!!')

# Allowed Hosts
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=['localhost'])

INTERNAL_IPS = ("127.0.0.1",)

# APP CONFIGURATION

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    # Useful template tags:
    # 'django.contrib.humanize',
    'dal',
    'dal_select2',

    # Admin
    'django.contrib.admin',
)

THIRD_PARTY_APPS = (
    'localflavor',
    'ckeditor',
    'widget_tweaks',
    'rest_framework',
    'django_filters',
    'drf_hal_json',
    'rest_framework_xml',
    'rest_framework_csv',
    'corsheaders',
    'simple_history'
)

# Apps specific for this project go here.
LOCAL_APPS = (
    'adesao',
    'gestao',
    'planotrabalho',
    'snc',
    'apiv2',
)

# App used on development process
DEVELOPMENT_SUPPORT_APPS = (
    'django_extensions',
    'debug_toolbar',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

if DEBUG:
    INSTALLED_APPS = INSTALLED_APPS + DEVELOPMENT_SUPPORT_APPS

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'apiv2.pagination.HalLimitOffsetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PARSER_CLASSES':
        ('rest_framework_xml.parsers.XMLParser',),
    'DEFAULT_RENDERER_CLASSES': (
        'drf_hal_json.renderers.JsonHalRenderer',
        'rest_framework_xml.renderers.XMLRenderer',
        'rest_framework_csv.renderers.CSVRenderer',
        'apiv2.renderers.XLSRenderer',
        'apiv2.renderers.ODSRenderer',
    ),

    'URL_FIELD_NAME': 'self',
}

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = (
    # Make sure djangosecure.middleware.SecurityMiddleware is listed first
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'adesao.middleware.ThreadLocalUserMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware'
)

if DEBUG:
    MIDDLEWARE = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE

CORS_ORIGIN_ALLOW_ALL = True

# MIGRATIONS CONFIGURATION
# ------------------------------------------------------------------------------
# MIGRATION_MODULES = {
#     'sites': 'sistema-nacional-cultura.contrib.sites.migrations'
# }

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
# FIXTURE_DIRS = (
#     str(ROOT_DIR.path('fixtures')),
# )

# EMAIL CONFIGURATION
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='naoresponda@turismo.gov.br')
EMAIL_USE_TLS = True
EMAIL_HOST = env('EMAIL_HOST', default='mailapp.cultura.gov.br')
EMAIL_PORT = env('EMAIL_PORT', default=25)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='srv_salic')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='emailSalic')
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# MANAGER CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ("""Ronald P Jr""", 'ronald.junior@basis.com.br'),
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': env.db("DATABASE_URL", default="postgres://postgres:postgres123@localhost/dbsnc")
}

DATABASES['default']['ATOMIC_REQUESTS'] = True


# GENERAL CONFIGURATION
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'pt-br'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 2

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(ROOT_DIR.path('snc/templates')),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                # 'allauth.account.context_processors.account',
                # 'allauth.socialaccount.context_processors.socialaccount',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Your stuff: custom template context processors go here
            ],
        },
    },
]

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [
    str(ROOT_DIR.path('snc/static')),
]

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(ROOT_DIR('media'))
FILE_UPLOAD_PERMISSIONS = 0o644

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'snc.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
# WSGI_APPLICATION = 'config.wsgi.application'

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    # 'allauth.account.auth_backends.AuthenticationBackend',
)

# Some really nice defaults
# ACCOUNT_AUTHENTICATION_METHOD = 'username'
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

# Custom user app defaults
# Select the correct user model
# AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = 'adesao:home'
LOGIN_URL = 'adesao:login'
LOGOUT_URL = 'adesao:logout'

# Your common stuff: Below this line define 3rd party library settings
USE_DJANGO_JQUERY = False
JQUERY_URL = STATIC_URL + 'js/jquery.min.js'

CKEDITOR_JQUERY_URL = JQUERY_URL
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source']
        ]
    },
}

PIWIK_SITE_ID = 1
PIWIK_URL = ''

RECEITA_URL = env("RECEITA_URL", default='http://sistemasweb.cultura.gov.br/minc-pessoa/servicos/pessoa_juridica/consultar/')
RECEITA_USER = env("RECEITA_USER", default='')
RECEITA_PASSWORD = env("RECEITA_PASSWORD", default='')

if env("SENTRY_DSN"):
    sentry_sdk.init(
            dsn=env("SENTRY_DSN"),
            integrations=[DjangoIntegration()],
            send_default_pii=True
            )
