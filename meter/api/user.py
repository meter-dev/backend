from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from meter.api import get_user_service, get_current_user
from meter.domain.user import UserService, UserSignup, User

router = APIRouter()


class SignupResponse(BaseModel):
    id: str


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    input: UserSignup,
    svc: Annotated[UserService, Depends(get_user_service)],
):
    id = svc.signup(input)
    return SignupResponse(id=id)


@router.get('/me')
async def get_user(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.patch("/{id}")
async def update_user(id: str):
    """
    Update user properties
    """
    pass


@router.post("/verify-email")
async def verify_email():
    pass
