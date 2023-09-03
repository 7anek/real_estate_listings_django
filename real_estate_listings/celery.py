from celery import Celery


app = Celery('real_estate_listings')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()