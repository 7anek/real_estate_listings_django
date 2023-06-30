"""
Django settings for real_estate_listings project.

Generated by 'django-admin startproject' using Django 4.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import sys
from corsheaders.defaults import default_headers
# sys.path.append('scraper')
from datetime import timedelta
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG') == 'TRUE'
# DEBUG = True
TESTING = 'test' in sys.argv
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
SCRAPYD_URL = os.environ.get('SCRAPYD_URL')
SCRAPYD_PROJECT = os.environ.get('SCRAPYD_PROJECT')

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

# tak działa:
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('PG_DBNAME'),
        'USER': os.environ.get('PG_USER'),
        'PASSWORD': os.environ.get('PG_PASSWORD'),
        'HOST': os.environ.get('PG_HOST'),
        'PORT': os.environ.get('PG_PORT'),
        # 'TEST': {
        #     'MIRROR': 'test'
        #     # 'NAME': os.environ.get('PG_TEST_DBNAME'),
        # }
    },
    # 'test': {
    #     # 'ENGINE': 'django.contrib.gis.db.backends.postgis',
    #     # # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     # 'NAME': os.environ.get('PG_TEST_DBNAME'),
    #     # 'USER': os.environ.get('PG_TEST_USER'),
    #     # 'PASSWORD': os.environ.get('PG_TEST_PASSWORD'),
    #     # 'HOST': os.environ.get('PG_TEST_HOST'),
    #     # 'PORT': os.environ.get('PG_TEST_PORT'),
    #     # 'TEST': {
    #     #     'NAME': os.environ.get('PG_TEST_DBNAME'),  # Użyj istniejącej bazy danych testowej
    #     # },
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': 'only4test.sqlite'
    # }
}

if TESTING:
    DATABASES['default'] = {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('PG_LOCAL_DBNAME'),
        'USER': os.environ.get('PG_LOCAL_USER'),
        'PASSWORD': os.environ.get('PG_LOCAL_PASSWORD'),
        'HOST': os.environ.get('PG_LOCAL_HOST'),
        'PORT': os.environ.get('PG_LOCAL_PORT'),
    }

# AUTH_USER_MODEL = 'your_app_name.User'

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
STATIC_ROOT = f"{BASE_DIR}/properties/static/"

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
# AWS_DEFAULT_ACL = 'public-read'
AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.eu-north-1.amazonaws.com'
# AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
# AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400', 'ACL': 'public-read'}

# s3 static settings
# AWS_LOCATION = 'static'
AWS_LOCATION = ''
# STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://localhost:3000",
    "http://127.0.0.1:3000",
    "https://127.0.0.1:3000",
]
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
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        # 'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

# SIMPLE_JWT = {
#     "ACCESS_TOKEN_LIFETIME": timedelta(seconds=20),
#     "REFRESH_TOKEN_LIFETIME": timedelta(seconds=40),
# }

LOGIN_REDIRECT_URL = "home"
