from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from meter.api import auth, comment, get_config, group, issue, rule, upload, user
from meter.api.cors import set_cors
from meter.domain import create_db_and_tables, get_engine
from meter.exception import CustomErrorException
from meter.helper import get_message_by_response_code

app = FastAPI()
set_cors(app, get_config().cors)


@app.get("/")
def index():
    # TODO: maybe return some information about this service?
    return ""


@app.get("/healthz")
def health_check():
    return "ok"


@app.get("/readyz")
def readiness_check():
    return "ok"


@app.on_event("startup")
def on_startup():
    cfg = get_config()
    create_db_and_tables(get_engine(cfg.sql))


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": exc.args[0]},
    )


@app.exception_handler(CustomErrorException)
async def custom_exception_handler(request: Request, exc: CustomErrorException):
    return JSONResponse(
        status_code=400,
        content={
            "message": get_message_by_response_code(exc.response_code),
            "code": exc.response_code.value,
        },
    )


apis = (
    ("/rule", rule),
    ("/auth", auth),
    ("/comment", comment),
    ("/issue", issue),
    ("/upload", upload),
    ("/user", user),
    ("/group", group),
)

for prefix, api in apis:
    app.include_router(api.router, prefix=prefix)
