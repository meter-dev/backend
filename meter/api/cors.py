from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class CORSConfig(BaseModel):
    allow_origins: list[str] | None
    allow_origin_regex: str | None


def set_cors(app: FastAPI, config: CORSConfig | None):
    if config is None:
        return
    cors_args = {k: v for k, v in config.dict().items() if v is not None}
    app.add_middleware(
        CORSMiddleware,
        allow_methods=[
            "OPTIONS",
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "HEAD",
            "PATCH",
        ],
        allow_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        **cors_args,
    )
