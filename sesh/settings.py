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
import sys
from celery.schedules import crontab
from datetime import timedelta
from ConfigParser import RawConfigParser
import djcelery

djcelery.setup_loader()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.join(BASE_DIR,'seshdash')
TEMPLATE_DIR = os.path.join(BASE_DIR,'templates')
LOG_DIR = os.path.join(BASE_DIR,'logs')
CONFIG_FILE =  os.path.join(BASE_DIR,'settings_local.ini')

if not os.path.isfile(CONFIG_FILE):
    print "Using temp config file"
    CONFIG_FILE =  os.path.join(BASE_DIR,'settings_local_example.ini')

# Initialize config reader with defaults
config = RawConfigParser(
       {
               'ENGINE':'django.db.backends.sqlite3',
               'NAME' : 'SESH_DB',
               'USER':'',
               'PASSWORD':'',
               'HOSTNAME':'',
               'HOST':'',
               'PORT':'',
               'USERNAME':'',
               'PASSWORD':'',
               'DB':'',
               'LOGGING_LEVEL':'DEBUG',
               'SECRET_KEY':'5dsf0sfg5243dfgr26',
               'DEV_MODE': True,
               'EMAIL_USE_TLS':True,
               'EMAIL_HOST':'smtp.gmail.com',
               'EMAIL_PORT':587,
               'EMAIL_HOST_USER':'USER',
               'EMAIL_HOST_PASSWORD':'PASSWORD',
               'EMAIL_HOST_BACKEND':'django.core.mail.backends.smtp.EmailBackend',
               'FROM_EMAIL':'some_email@gmail.com',
               'FORCAST_KEY':'ASDASFAG',
               'TOKEN':'asdasdasd',
               'CLICKATELL_KEY':'',
               'SLACK_TEST_KEY':''
               }
        )

config.read( os.path.join(BASE_DIR,CONFIG_FILE))

# quick-start development settings - unsuitable for production
# see https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# security warning: keep the secret key used in production secret!
SECRET_KEY = config.get('system','SECRET_KEY')

# security warning: don't run with debug turned on in production!
DEBUG = eval(config.get('system','DEV_MODE_ON'))


ALLOWED_HOSTS = [config.get('system','ALLOWED_HOSTS') ]

# weather key
FORECAST_KEY = config.get('api','forecast_key')

# slack key
SLACK_TEST_KEY = config.get('api', 'slack_test_key')

# Temp folder for misc files

try:
    TEMP_FOLDER = config.get('system','temp_folder')
except:
    TEMP_FOLDER = "/tmp/"

# sms API key
CLICKATELL_KEY = config.get('api','clickatell_key')

DATABASES = {
    'default': {
        'ENGINE': config.get('database','ENGINE'),
        'NAME': config.get('database','NAME'),
        'USER': config.get('database','USER'),
        'PASSWORD': config.get('database','PASSWORD'),
        'HOST': config.get('database','HOST'),
    }
}
#influx settings
INFLUX_HOST = config.get('influx','HOST')
INFLUX_PORT = config.get('influx','PORT')
INFLUX_USERNAME =  config.get('influx','USERNAME')
INFLUX_PASSWORD = config.get('influx','PASSWORD')
INFLUX_DB = config.get('influx','DB')

# Guardian settings
ANONYMOUS_USER_ID = -1

# celery settings
BROKER_URL = 'redis://localhost:6379/0'
#celery_result_backend = 'redis://localhost/0'
CELERY_RESULT_BACKEND = 'djcelery.backends.database.DatabaseBackend'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler' # needed for djcelery admin
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Kigali'
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
    'get_aggregate_daily_data': {
        'task': 'seshdash.tasks.get_aggregate_daily_data',
        'schedule': crontab(hour=0, minute=0),
        'args': None,
    },
    'get_send_reports': {
        'task': 'seshdash.tasks.send_reports',
        'schedule': crontab(hour=0, minute=30, day_of_week=6),
        'args': ['week'],
    },
    'get_send_reports': {
        'task': 'seshdash.tasks.send_reports',
        'schedule': crontab(hour=0, minute=30),
        'args': ['day'],
    },
    'alert_checker': {
        'task': 'seshdash.tasks.alert_engine',
        'schedule': timedelta(minutes=5),
        'args': '',
     'rmc_status': {
        'task': 'seshdash.tasks.rmc_status_update',
        'schedule': timedelta(minutes=5),
        'args': '',
    },   },
}
#authentication
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login'
#mail
EMAIL_USE_TLS = True
EMAIL_HOST = config.get('mail','EMAIL_HOST')
EMAIL_PORT = config.get('mail','EMAIL_PORT')
EMAIL_HOST_USER = config.get('mail','EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config.get('mail','EMAIL_HOST_PASSWORD')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#email_templates_dir = os.path.join(template_dir,'email')
FROM_EMAIL = config.get('mail','FROM_EMAIL')


LOGGING_LEVEL = config.get('system','LOGGING_LEVEL')

'''
#logging
LOGGING = {
        'version':1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                'datefmt' : "%d/%b/%Y %H:%M:%S"
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers':
            {
            'file':{
                    'level': 'DEBUG',
                    'class': 'logging.FileHandler',
                    'filename':os.path.join(LOG_DIR, "all.log")
                },
            'celery_file':{
                    'level': 'DEBUG',
                    'class': 'logging.FileHandler',
                    'filename': os.path.join(LOG_DIR , "celery.log")

                },
            'console':{
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                },

            'default': {
                'level':'DEBUG',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(LOG_DIR , "celery_default.log"),
                'maxBytes': 1024*1024*5, # 5 MB
                'backupCount': 5,
                'formatter':'simple',
                }
            },
        'loggers':{
            'django.db.backends':
                {
                'handler':['file'],
                 'level': LOGGING_LEVEL,
                 'filename' : True
                },
            'django':{
                'handler':['file'],
                'level': LOGGING_LEVEL,
                'propogate':True
                },
            '':{
                 'handler':['default'],
                 'level': 'DEBUG',
                 'propogate':True
                }
            }
        }
   
'''

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': LOGGING_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            
        },
        'file':{
           'level': 'DEBUG',
           'class': 'logging.FileHandler',
           'filename':os.path.join(LOG_DIR, "all.logs"),
           'formatter': 'verbose',
        },
    },

    'loggers': {
        'django': {
            'handlers': ['console'],
        },
        'seshdash': {
            'handlers': ['console', 'file'],
            'level': LOGGING_LEVEL,
        }    
    }
    
} 

    
# Error reporting
if not DEBUG:
     print "rollbar enabled"
     ROLLBAR = {
             'access_token': config.get('rollbar','token'),
             'environment': 'development' if DEBUG else 'production',
             'root': BASE_DIR,
             }

     import rollbar
     rollbar.init(**ROLLBAR)


# application definition
INSTALLED_APPS = (
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
    'geoposition',
    'djcelery',
    'django_extensions',

)

#BOWER
BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR,'components')
BOWER_INSTALLED_APPS = (
            'jquery#2.2.1',
            'jquery-ui#1.11.4',
            'mapbox.js#2.4.0',
            'd3#3.5.16',
            'nvd3#1.7.1',
            'moment#2.11.2',
            'highcharts-release#4.2.4',
            'bootstrap#3.3.6',
            'font-awesome#4.6.1',
            'metisMenu#2.5.0',
            'morrisjs#0.5.1',
            'raphael#2.2.0',
            'react#0.14.8',
            'babel#d54d59ff74',
            'awesomplete#1.1.0',
            'pace#1.0.2',
            )

ANONYMOUS_USER_ID = -1

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

if not DEBUG:
    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
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


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = CELERY_TIMEZONE

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

STATICFILES_FINDERS = (
                        "django.contrib.staticfiles.finders.FileSystemFinder",
                        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
                        "djangobower.finders.BowerFinder",)

GEOPOSITION_MAP_OPTIONS = {
    'minZoom': 3,
    'maxZoom': 15,
}

GEOPOSITION_MARKER_OPTIONS = {
    'cursor': 'move'
}
