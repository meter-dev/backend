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
from meter.helper import raise_unauthorized_exception

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
    access_token = auth_svc.sign(data={"sub": user.name})
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
    verify_email = cfg.verify_email
    access_token_expires = timedelta(minutes=verify_email.expire)
    access_token = auth_svc.sign(
        data={"sub": user.name},
        expires_after=access_token_expires,
    )
    callback_url = f'{cfg.host}{router.url_path_for("active")}?token={access_token}'
    with open(verify_email.template_path, "r") as f:
        template = f.read()
    content = template.format(callback_url=callback_url)
    email_svc.send_noreply(
        [user.email],
        verify_email.subject,
        content,
    )
    return access_token


@router.get("/active", status_code=status.HTTP_204_NO_CONTENT)
async def active(
    token: str,
    user_svc: Annotated[UserService, Depends(get_user_service)],
    auth_svc: Annotated[AuthService, Depends(get_auth_service)],
):
    """Activate a user."""
    try:
        payload = auth_svc.decode_jwt(token)
        username: str = payload.get("sub")
        if username is None:
            raise_unauthorized_exception()
    except JWTError:
        raise_unauthorized_exception()
    user = user_svc._get_by_name(username)
    if user.active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User Has Been Actived")
    if user is None:
        raise_unauthorized_exception()
    user_svc.activate(user)
