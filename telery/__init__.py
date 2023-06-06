from celery import Celery

app = Celery("telery")
app.config_from_object("celeryconfig")
