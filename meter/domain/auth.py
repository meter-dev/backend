from datetime import datetime, timedelta
from typing import Any

from jose import jwt
from pydantic import BaseModel


class AuthConfig(BaseModel):
    secret_key: str
    algorithm: str
    default_ttl_sec: int


class AuthService:

    def __init__(self, config: AuthConfig) -> None:
        self.config = config

    def sign(
        self,
        data: dict[str, Any],
        expires_after: timedelta | None = None,
    ):
        if expires_after is None:
            expires_after = timedelta(seconds=self.config.default_ttl_sec)
        expires_at = datetime.now() + expires_after
        to_encode = data.copy() | {'exp': expires_at}
        return jwt.encode(
            to_encode,
            self.config.secret_key,
            algorithm=self.config.algorithm,
        )

    def decode_jwt(self, token):
        payload = jwt.decode(token,
                             self.config.secret_key,
                             algorithms=self.config.algorithm)
        return payload
