"""
Django settings for real_estate_listings project.

Generated by 'django-admin startproject' using Django 4.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import sys
import logging
from corsheaders.defaults import default_headers
# sys.path.append('scraper')
from datetime import timedelta
from pathlib import Path
import os
# from dotenv import load_dotenv
#
# load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = os.environ.get('DEBUG') == 'TRUE'
IS_DOCKER = os.environ.get("IS_DOCKER", False)
# DEBUG = True
TESTING = 'test' in sys.argv
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
# SCRAPYD_URL = "http://django:6800"
SCRAPYD_URL = "http://localhost:6800"
SCRAPYD_PROJECT = "default"

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    "crispy_bootstrap4",
    'accounts',
    'properties_scrapy',
    'properties_api',
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django.contrib.gis',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'real_estate_listings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'properties_scrapy.context_processors.google_maps_api_key',
            ],
        },
    },
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"

WSGI_APPLICATION = 'real_estate_listings.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# PGSERVICEFILE=os.environ.get('PGSERVICEFILE')
# PGPASSFILE=os.environ.get('PGPASSFILE')
# Taka kofiguracja niedziała w scrapy, ale działa w django i jest według  dokumentacji django
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'OPTIONS': {
#             'service': 'pg_service',
#             'passfile': '.pgpass',
#         }
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.contrib.gis.db.backends.postgis',
#         'NAME': os.environ.get('PG_DBNAME'),
#         'USER': os.environ.get('PG_USER'),
#         'PASSWORD': os.environ.get('PG_PASSWORD'),
#         'HOST': "db" if IS_DOCKER else os.environ.get('PG_HOST'),
#         'PORT': os.environ.get('PG_PORT'),
#     }
# }

# AUTH_USER_MODEL = 'your_app_name.User'
AUTH_USER_MODEL = 'accounts.CustomUser'

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Europe/Warsaw'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

# STATIC_URL = 'static/'
# # STATIC_ROOT = "/home/janek/PycharmProjects/property_scraper_api/properties/static/"
# STATIC_ROOT = f"{BASE_DIR}/properties/static/"
# STATIC_ROOT = f"{BASE_DIR}/static/"
STATIC_ROOT = '/app/static/'
STATIC_URL = "static/"

# AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
# # AWS_DEFAULT_ACL = 'public-read'
# AWS_DEFAULT_ACL = None
# AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.eu-north-1.amazonaws.com'
# # AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
# AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
# # AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400', 'ACL': 'public-read'}
#
# # s3 static settings
# # AWS_LOCATION = 'static'
# AWS_LOCATION = ''
# # STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
# STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('PG_DBNAME'),
        'USER': os.environ.get('PG_USER'),
        'PASSWORD': os.environ.get('PG_PASSWORD'),
        'HOST': os.environ.get('PG_HOST'),
        'PORT': os.environ.get('PG_PORT'),
    }
}
print(DATABASES)
print(os.environ.get('DJANGO_SETTINGS_MODULE'))

# SCRAPEOPS_API_KEY = os.getenv('SCRAPEOPS_API_KEY')
# EXTENSIONS = {
#     'scrapeops_scrapy.extension.ScrapeOpsMonitor': 500,
# }
# DOWNLOADER_MIDDLEWARES = {
#     'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550,
#     'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
# }
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CSRF_TRUSTED_ORIGINS = [
#     "http://localhost:3000",
#     "https://localhost:3000",
#     "http://127.0.0.1:3000",
#     "https://127.0.0.1:3000",
# ]
#
# CORS_ORIGIN_WHITELIST = [
#     "http://localhost:3000",
#     "https://localhost:3000",
#     "http://127.0.0.1:3000",
#     "https://127.0.0.1:3000",
# ]
# CORS_ALLOW_HEADERS = list(default_headers)
# CSRF_COOKIE_SECURE=False
# SESSION_COOKIE_SECURE=False

# dotyczą widoków, które dziedziczą z widoków dostarczonych przez DRF.
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        # 'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailorUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# SIMPLE_JWT = {
#     "ACCESS_TOKEN_LIFETIME": timedelta(seconds=20),
#     "REFRESH_TOKEN_LIFETIME": timedelta(seconds=40),
# }

LOGIN_REDIRECT_URL = "home"

# Konfiguracja loggera
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Utworzenie obsługi logowania do pliku
logs_path = 'django.log' if IS_DOCKER else 'logs/django.log'
# file_handler = logging.FileHandler('django.log')
file_handler = logging.FileHandler(logs_path)

file_handler.setLevel(logging.DEBUG)

# Dodanie obsługi logowania do loggera
logger.addHandler(file_handler)

# Ustawienie loggera Django na zdefiniowany logger
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            # 'filename': 'django.log',
            'filename': logs_path,
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',
    },
}

# LIVE_SERVER_PORT = 8000
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
