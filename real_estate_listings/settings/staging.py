from dotenv import load_dotenv,find_dotenv
load_dotenv(find_dotenv("env/.env.stg"))
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
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = default_headers + (
    "ngrok-skip-browser-warning",
)
HOST_URL="localhost:8000"
HOST_SCHEME="http"





