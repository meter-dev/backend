from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from meter.api import get_auth_service, get_user_service, get_current_user
from meter.domain.auth import AuthService
from meter.domain.user import UserLogin, UserService, User
from meter.domain.smtp import send_noreply
from jose import JWTError

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


@router.post('/send_email')
async def send_email(
    user: Annotated[User, Depends(get_current_user)],
    auth_svc: Annotated[AuthService, Depends(get_auth_service)],
):
    if user.active:
        return HTTPException(status.HTTP_400_BAD_REQUEST,
                             'User Has Been Actived')
    access_token_expires = timedelta(minutes=10)
    access_token = auth_svc.sign(
        data={'sub': user.name},
        expires_after=access_token_expires,
    )
    # TODO: need to be changed to the real address
    verify_link = f'https://noj.tw/api/auth/active/{access_token}'
    send_noreply([user.email], '[Meter] Varify Your Email', verify_link)
    return access_token


@router.get('/active')
async def active(
    token: str,
    user: Annotated[User, Depends(get_current_user)],
    user_svc: Annotated[UserService, Depends(get_user_service)],
    auth_svc: Annotated[AuthService, Depends(get_auth_service)],
):
    '''Activate a user.
    '''
    if user.active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            'User Has Been Actived')
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
    if user.name != username:
        raise credentials_exception
    user_svc.activate(user)
