from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.engine import Engine
from sqlmodel import Session

from meter.domain import get_engine
from meter.domain.auth import AuthConfig, AuthService
from meter.domain.user import UserService
from jose import JWTError

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/auth/token', scheme_name="JWT")


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


def get_current_user(
    token: Annotated[str, Depends(oauth2_schema)],
    user_svc: Annotated[UserService, Depends(get_user_service)],
    auth_svc: Annotated[AuthService, Depends(get_auth_service)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth_svc.decode_jwt(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = user_svc._get_by_name(username)
    if user is None:
        raise credentials_exception
    return user
