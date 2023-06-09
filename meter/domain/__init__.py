from pydantic import BaseModel, EmailStr
from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, create_engine


class SQLEngineParam(BaseModel):
    url: str
    connect_args: dict


class VerifyEmailParam(BaseModel):
    subject: str
    template_path: str
    expire: int


class SMTPServerParam(BaseModel):
    server: str
    port: int
    noreply: EmailStr
    noreply_password: str | None


def get_engine(param: SQLEngineParam):
    engine = create_engine(**param.dict())
    return engine


# TODO: this might not be the correct type?
# https://github.com/tiangolo/sqlmodel/blob/43a689d369f52b72aac60efd71111aba7d84714d/sqlmodel/engine/create.py#L78
def create_db_and_tables(engine: Engine):
    SQLModel.metadata.create_all(engine)
