from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(".env.prod"))

from .base import *
from corsheaders.defaults import default_headers

FRONTEND_DOMAIN = os.environ.get('FRONTEND_URL')
HOST_DOMAIN = os.environ.get('NGROK_URL')
HOST_SCHEME = "https"
PRODUCTION = True
DEBUG = False

# STATIC_URL = f"{HOST_SCHEME}://{HOST_DOMAIN}/static/"

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators
CORS_ALLOWED_ORIGINS = [
    f"http://{FRONTEND_DOMAIN}",
    f"https://{HOST_DOMAIN}",
    "http://localhost:3000",
    "https://localhost:3000",
    "http://127.0.0.1:3000",
    "https://127.0.0.1:3000",
]
# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOW_ALL_ORIGINS = True

# CSRF_TRUSTED_ORIGINS = [
#     f"http*://{FRONTEND_URL}",
#     f"http*://{HOST_URL}"
# ]

# CSRF_TRUSTED_ORIGINS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "http://real-estate-listings-frontend.vercel.app",
    "https://real-estate-listings-frontend.vercel.app",
    "http://blessed-flea-crisp.ngrok-free.app",
    "https://blessed-flea-crisp.ngrok-free.app",
    "http://localhost",
    "https://localhost"
]
# CORS_ALLOWED_ORIGIN_REGEXES = [
#     r"^https?://\.+\.ngrok\-free\.app(:\d+)?$"
# ]
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

ALLOWED_HOSTS = [FRONTEND_DOMAIN, HOST_DOMAIN, 'localhost', '127.0.0.1']
# ALLOWED_HOSTS = ['*']

# CORS_ALLOW_METHODS = [
#     "DELETE",
#     "GET",
#     "OPTIONS",
#     "PATCH",
#     "POST",
#     "PUT",
# ]

# CORS_ALLOW_HEADERS = [
#     "accept",
#     "accept-encoding",
#     "authorization",
#     "content-type",
#     "dnt",
#     "origin",
#     "user-agent",
#     "x-csrftoken",
#     "x-requested-with",
#     "ngrok-skip-browser-warning"  # jeśli włączam tunelowanie ngrok
# ]

CORS_ALLOW_HEADERS = default_headers + (
    "ngrok-skip-browser-warning",
)

# CORS_ORIGIN_REGEX_WHITELIST=(".*")


