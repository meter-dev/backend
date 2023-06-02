from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from pydantic import BaseModel

from meter.api import (
    MeterConfig,
    get_auth_service,
    get_config,
    get_current_user,
    get_email_service,
    get_user_service,
)
from meter.domain.auth import AuthService
from meter.domain.smtp import EmailService
from meter.domain.user import User, UserLogin, UserService

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/token")
async def new_access_token(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    user_svc: Annotated[UserService, Depends(get_user_service)],
    auth_svc: Annotated[AuthService, Depends(get_auth_service)],
):
    user = user_svc.login(
        UserLogin(
            name=form_data.username,
            password=form_data.password,
        )
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # TODO: config
    access_token_expires = timedelta(minutes=15)
    access_token = auth_svc.sign(
        data={"sub": user.name},
        expires_after=access_token_expires,
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
    )


@router.post("/send_email")
async def send_email(
    user: Annotated[User, Depends(get_current_user)],
    auth_svc: Annotated[AuthService, Depends(get_auth_service)],
    cfg: Annotated[MeterConfig, Depends(get_config)],
    email_svc: Annotated[EmailService, Depends(get_email_service)],
):
    if user.active:
        return HTTPException(status.HTTP_400_BAD_REQUEST, "User Has Been Actived")
    access_token_expires = timedelta(minutes=60)
    access_token = auth_svc.sign(
        data={"sub": user.name},
        expires_after=access_token_expires,
    )
    verify_email = cfg.verify_email
    email_svc.send_noreply(
        [user.email],
        verify_email.subject,
        verify_email.content.format(access_token=access_token),
    )
    return access_token


@router.get("/active")
async def active(
    token: str,
    user_svc: Annotated[UserService, Depends(get_user_service)],
    auth_svc: Annotated[AuthService, Depends(get_auth_service)],
):
    """Activate a user."""
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
    if user.active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User Has Been Actived")
    if user is None:
        raise credentials_exception
    user_svc.activate(user)
