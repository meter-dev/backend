from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.engine import Engine
from sqlmodel import Session

from meter.config import MeterConfig
from meter.domain import get_engine as _get_engine
from meter.domain.auth import AuthService
from meter.domain.rule import RuleService
from meter.domain.smtp import EmailService
from meter.domain.user import UserService
from meter.helper import raise_unauthorized_exception

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/token", scheme_name="JWT")


def get_config():
    return MeterConfig()


def get_engine(cfg: Annotated[MeterConfig, Depends(get_config)]):
    return _get_engine(cfg.sql)


def get_session(engine: Annotated[Engine, Depends(get_engine)]):
    with Session(engine) as session:
        yield session


def get_user_service(session: Annotated[Session, Depends(get_session)]):
    return UserService(session)


def get_auth_service(cfg: Annotated[MeterConfig, Depends(get_config)]):
    return AuthService(cfg.auth)


def get_email_service(cfg: Annotated[MeterConfig, Depends(get_config)]):
    return EmailService(cfg.smtp)


def get_rule_service(session: Annotated[Session, Depends(get_session)]):
    return RuleService(session)


def get_current_user(
    token: Annotated[str, Depends(oauth2_schema)],
    user_svc: Annotated[UserService, Depends(get_user_service)],
    auth_svc: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        payload = auth_svc.decode_jwt(token)
        username: str = payload.get("sub")
        if username is None:
            raise_unauthorized_exception()
    except JWTError:
        raise_unauthorized_exception()
    user = user_svc._get_by_name(username)
    if user is None:
        raise_unauthorized_exception()
    return user
