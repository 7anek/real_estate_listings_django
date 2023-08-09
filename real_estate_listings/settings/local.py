from .base import *

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "https://localhost:3000",
#     "http://127.0.0.1:3000",
#     "https://127.0.0.1:3000",
# ]
AUTH_PASSWORD_VALIDATORS = []
ALLOWED_HOSTS = ['*']
# CORS_ALLOWED_ORIGIN_REGEXES = [
#     r"^https?://\.+\.ngrok\-free\.app(:\d+)?$",
# ]
CORS_ORIGIN_ALLOW_ALL = True