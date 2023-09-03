from dotenv import load_dotenv,find_dotenv
load_dotenv(find_dotenv("env/.env.dev"))
from .base import *
from corsheaders.defaults import default_headers



PRODUCTION=False
DEBUG=True
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
HOST_URL="localhost:8000"
HOST_SCHEME="http"
CORS_ALLOW_HEADERS = default_headers + (
    "ngrok-skip-browser-warning",
)



CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
