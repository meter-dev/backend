import toml
from pydantic import BaseSettings

from meter.domain import SMTPServerParam, SQLEngineParam, VerifyEmailParam
from meter.domain.auth import AuthConfig


def toml_settings(settings: BaseSettings) -> dict:
    try:
        return toml.load(open(settings.__config__.path))
    except FileNotFoundError:
        # if config file does not exist, fallback to other config sources
        return {}


class MeterConfig(BaseSettings):
    sql: SQLEngineParam
    auth: AuthConfig
    verify_email: VerifyEmailParam
    SMTP: SMTPServerParam

    class Config:
        path = "meter.toml"

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                toml_settings,
                env_settings,
                file_secret_settings,
            )
