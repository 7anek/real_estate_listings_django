try:
    from celery import Celery
except ModuleNotFoundError as e:
    print("Celery package not found. Installing...")
    import subprocess
    subprocess.call(["pip", "install", "celery"])
    from celery import Celery

app = Celery('real_estate_listings')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()