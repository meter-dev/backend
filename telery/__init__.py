from celery import Celery

from . import celeryconfig

app = Celery("telery")
app.config_from_object(celeryconfig)
