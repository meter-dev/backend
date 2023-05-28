from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from meter.api import (
    alert_rule,
    auth,
    comment,
    get_config,
    group,
    issue,
    upload,
    user,
)
from meter.domain import create_db_and_tables, get_engine

app = FastAPI()


@app.get('/')
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
    # FIXME: we might need to mock the config, but startup event can't use Depends
    cfg = get_config()
    create_db_and_tables(get_engine(cfg.sql))


@app.exception_handler(IntegrityError)
async def unicorn_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={'message': exc.args[0]},
    )


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
