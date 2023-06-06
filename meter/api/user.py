from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from meter.api import get_current_user, get_user_service
from meter.domain.user import User, UserService, UserSignup
from meter.constant.response_code import ResponseCode
from meter.helper import raise_custom_exception
from sqlalchemy.exc import IntegrityError

router = APIRouter()


class SignupResponse(BaseModel):
    id: str


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    input: UserSignup,
    svc: Annotated[UserService, Depends(get_user_service)],
):
    try:
        id = svc.signup(input)
    except IntegrityError as e:
        orig = str(e.orig)
        if "name" in orig:
            raise_custom_exception(ResponseCode.USER_SIGNUP_DUPLICATE_USERNAME_1301)
        elif "email" in orig:
            raise_custom_exception(ResponseCode.USER_SIGNUP_DUPLICATE_EMAIL_1302)
        raise e
    return SignupResponse(id=id)


@router.patch("/{id}")
async def update_user(id: str):
    """
    Update user properties
    """
    pass
