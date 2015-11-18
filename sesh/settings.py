"""
Django settings for sesh project.

Generated by 'django-admin startproject' using Django 1.8.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""
from __future__ import absolute_import

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from celery.schedules import crontab
from datetime import timedelta
from ConfigParser import RawConfigParser


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR,'templates')

config = RawConfigParser()
config.read( os.path.join(BASE_DIR,'settings_local.ini'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get('secret','SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

ENPHASE_KEY = config.get('api','ENPHASE_KEY')
FORECAST_KEY = config.get('api','FORECAST_KEY')

DATABASES = {
    'default': {
        'ENGINE': config.get('database','ENGINE'),
        'NAME': config.get('database','NAME'),
        'USER': config.get('database','USER'),
        'PASSWORD': config.get('database','PASSWORD'),
        'HOST': config.get('database','HOST'),
    }
}

# CELERY SETTINGS
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Kigali'
#TODO Move time constants to config file
CELERYBEAT_SCHEDULE = {
   'get_daily_weather_forecast': {
        'task': 'seshdash.tasks.get_weather_data',
        'schedule': timedelta(hours=5),
        'args': None,
    },
    'get_BOM_data': {
        'task': 'seshdash.tasks.get_BOM_data',
        'schedule': timedelta(minutes=5),
        'args': None,
    },
}

#Authentication
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login'

#Mail
EMAIL_USE_TLS = True
EMAIL_HOST = config.get('mail','EMAIL_HOST')
EMAIL_PORT = config.get('mail','EMAIL_PORT')
EMAIL_HOST_USER = config.get('mail','EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config.get('mail','EMAIL_HOST_PASSWORD')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Application definition
INSTALLED_APPS = (
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'seshdash',
    'guardian',
    'djangobower',
    'django_nvd3',
    'rest_framework',
    'rest_framework.authtoken',
)

#BOWER
BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR,'components')
BOWER_INSTALLED_APPS = (
            'jquery#1.9',
            'mapbox.js',
            'd3#3.3.13',
            'nvd3#1.7.1',
            )

ANONYMOUS_USER_ID = None

AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'guardian.backends.ObjectPermissionBackend',
        )

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'sesh.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.core.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'sesh.wsgi.application'

#ADMIN UI SETTINGS
GRAPPELLI_ADMIN_TITLE = "SESH Administration Dashboard"


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Kigali'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_FINDERS = (
                        "django.contrib.staticfiles.finders.FileSystemFinder",
                        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
                        "djangobower.finders.BowerFinder",)
