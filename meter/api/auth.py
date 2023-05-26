from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from meter.api import get_auth_service, get_user_service
from meter.domain.auth import AuthService
from meter.domain.user import UserLogin, UserService

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post('/token')
async def new_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm,
                         Depends(), ],
    user_svc: Annotated[UserService, Depends(get_user_service)],
    auth_svc: Annotated[AuthService, Depends(get_auth_service)],
):

    user = user_svc.login(
        UserLogin(
            name=form_data.username,
            password=form_data.password,
        ))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    # TODO: config
    access_token_expires = timedelta(minutes=15)
    access_token = auth_svc.sign(
        data={'sub': user.name},
        expires_after=access_token_expires,
    )
    return Token(
        access_token=access_token,
        token_type='bearer',
    )
