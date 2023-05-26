from typing import Optional

from passlib.hash import bcrypt
from pydantic import EmailStr
from sqlmodel import Field, Session, SQLModel, select


def verify_password(
    password: str,
    digest: str,
):
    return bcrypt.verify(password, digest)


def get_password_digest(password: str):
    return bcrypt.hash(password)


class UserBase(SQLModel):
    name: str = Field(index=True, unique=True, regex='^[a-zA-Z0-9_-]{2,32}$')
    email: EmailStr = Field(unique=True)


class User(UserBase, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    password_digest: str


class UserSignup(UserBase):
    password: str


class UserRead(UserBase):
    id: str


class UserLogin(SQLModel):
    name: str
    password: str


class UserService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def signup(self, input: UserSignup) -> str:
        user = User(
            name=input.name,
            email=input.email.lower(),
            password_digest=get_password_digest(input.password),
        )
        self.session.add(user)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        self.session.refresh(user)
        return user.id

    def get_by_id(self, id: str) -> UserRead | None:
        user = self.session.get(User, id)
        if not user:
            return None
        return UserRead.from_orm(user)

    def _get_by_name(self, name: str) -> User | None:
        users = self.session.exec(select(User).where(User.name == name))
        try:
            return next(users)
        except StopIteration:
            return None

    def _get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email.lower())
        users = self.session.exec(statement)
        try:
            return next(users)
        except StopIteration:
            return None

    def login(self, input: UserLogin) -> User | None:
        un = self._get_by_name(input.name)
        ue = self._get_by_email(input.name)
        user = un if un is not None else ue
        if user is None:
            return None
        if not verify_password(input.password, user.password_digest):
            return None
        return user
