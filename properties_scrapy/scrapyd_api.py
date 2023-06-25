from .scrapyd_singleton import ScrapydAPISingleton
from django.conf import settings

scrapyd = ScrapydAPISingleton(settings.SCRAPYD_URL)

