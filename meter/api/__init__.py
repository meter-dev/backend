from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.engine import Engine
from sqlmodel import Session

from meter.domain import get_engine
from meter.domain.auth import AuthConfig, AuthService
from meter.domain.user import UserService

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/auth/token')


# TODO: this might not be the correct type?
# https://github.com/tiangolo/sqlmodel/blob/43a689d369f52b72aac60efd71111aba7d84714d/sqlmodel/engine/create.py#L78
def get_session(engine: Annotated[Engine, Depends(get_engine)]):
    with Session(engine) as session:
        yield session


def get_user_service(session: Annotated[Session, Depends(get_session)]):
    return UserService(session)


def get_auth_service():
    # TODO: read from config file
    config = AuthConfig(
        secret_key='foobar',
        algorithm='HS256',
        default_ttl_sec=900,
    )
    return AuthService(config)
