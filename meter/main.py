from fastapi import FastAPI

from meter.api import (
    alert_rule,
    auth,
    comment,
    group,
    issue,
    upload,
    user,
)
from meter.domain import create_db_and_tables

app = FastAPI()


@app.get("/")
def index():
    # TODO: maybe return some information about this service?
    return ''


@app.get('/healthz')
def health_check():
    return 'ok'


@app.get('/readyz')
def readiness_check():
    return 'ok'


@app.on_event('startup')
def on_startup():
    create_db_and_tables()


apis = (
    ('/alert', alert_rule),
    ('/auth', auth),
    ('/comment', comment),
    ('/issue', issue),
    ('/upload', upload),
    ('/user', user),
    ('/group', group),
)

for (prefix, api) in apis:
    app.include_router(api.router, prefix=prefix)
