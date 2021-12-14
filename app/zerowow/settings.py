import os
import sentry_sdk
from distutils.util import strtobool
from celery.schedules import crontab
from pathlib import Path
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = strtobool(os.getenv('DEBUG', 'False'))
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(' ')
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', 3600 * 24 * 14))

ASGI_APPLICATION = 'zerowow.asgi.application'
ROOT_URLCONF = 'zerowow.urls'
AUTH_USER_MODEL = 'oauth.CustomUser'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/oauth/'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.environ['STATIC_ROOT']
MEDIA_ROOT = os.environ['MEDIA_ROOT']
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
TEMPLATES_DIRS = [os.path.join(BASE_DIR, 'templates')]

LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en-us')
USE_TZ = strtobool(os.getenv('USE_TZ', 'True'))
TIME_ZONE = os.getenv('TZ', 'UTC')
USE_I18N = True
USE_L10N = True

DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = strtobool(os.getenv('EMAIL_USE_TLS', 'False'))
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))

DISCORD_API_URL = os.environ['DISCORD_API_URL']
OAUTH_CLIENT_ID = os.environ['OAUTH_CLIENT_ID']
OAUTH_CLIENT_SECRET = os.environ['OAUTH_CLIENT_SECRET']
OAUTH_REDIRECT_URI = os.environ['OAUTH_REDIRECT_URI']
OAUTH_GRANT_TYPE = os.environ['OAUTH_GRANT_TYPE']
OAUTH_SCOPE = os.environ['OAUTH_SCOPE']

GOOGLE_SITE_PUBLIC = os.environ['GOOGLE_SITE_PUBLIC']
GOOGLE_SITE_SECRET = os.environ['GOOGLE_SITE_SECRET']

SITE_URL = os.environ['SITE_URL']
DISCORD_INVITE = os.environ['DISCORD_INVITE']
DISCORD_WEBHOOK = os.environ['DISCORD_WEBHOOK']
DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
DISCORD_SERVER_ID = os.environ['DISCORD_SERVER_ID']
DISCORD_OFFICER_ROLE = os.environ['DISCORD_OFFICER_ROLE']
DISCORD_MEMBER_ROLE = os.environ['DISCORD_MEMBER_ROLE']
DISCORD_CHANNEL_ID = os.environ['DISCORD_CHANNEL_ID']

TWITCH_CLIENT_ID = os.environ['TWITCH_CLIENT_ID']
TWITCH_CLIENT_SECRET = os.environ['TWITCH_CLIENT_SECRET']

CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_BACKEND']
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = os.getenv('TZ', 'UTC')

CELERY_BEAT_SCHEDULE = {
    'daily_cleanup': {
        'task': 'home.tasks.clear_sessions',
        'schedule': crontab(minute=0, hour=0),
    },
    'every-five-minutes': {
        'task': 'check_twitch_live',
        'schedule': crontab('*/2')
    },
}

if 'SENTRY_URL' in os.environ and os.environ['SENTRY_URL']:
    sentry_sdk.init(
        dsn=os.environ['SENTRY_URL'],
        integrations=[DjangoIntegration()],
        traces_sample_rate=float(os.getenv('SENTRY_SAMPLE_RATE', 0.25)),
        send_default_pii=True,
        debug=strtobool(os.getenv('SENTRY_DEBUG', os.getenv('DEBUG', 'False'))),
        environment=os.environ['SENTRY_ENVIRONMENT'],
    )

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis', 6379)],
        },
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ['CACHE_LOCATION'],
        'OPTIONS': {
            'PASSWORD': os.environ.get('CELERY_REDIS_PASSWORD'),
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASS'],
        'HOST': os.environ['DATABASE_HOST'],
        'PORT': os.environ['DATABASE_PORT'],
        'OPTIONS': {
            'isolation_level': 'repeatable read',
            'init_command': "SET sql_mode='STRICT_ALL_TABLES'",
        },
    },
}

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'home',
    'oauth',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': TEMPLATES_DIRS,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': ('%(asctime)s - '
                       '%(levelname)s - '
                       '%(filename)s '
                       '%(module)s.%(funcName)s:%(lineno)d - '
                       '%(message)s'),
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'app': {
            'handlers': ['console'],
            'level': os.getenv('APP_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
