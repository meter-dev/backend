from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.engine import Engine
from sqlmodel import Session

from meter.config import MeterConfig
from meter.domain import get_engine as _get_engine
from meter.domain.auth import AuthService
from meter.domain.user import UserService
from meter.domain.rule import RuleService

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/token")


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


def get_rule_service(session: Annotated[Session, Depends(get_session)]):
    return RuleService(session)
