import os
from pathlib import Path

import pytest
import toml
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from meter.api import get_config, get_email_service, get_session
from meter.config import MeterConfig
from meter.domain import (
    SMTPServerParam,
    SQLEngineParam,
    VerifyEmailParam,
    create_db_and_tables,
)
from meter.domain.auth import AuthConfig
from meter.domain.smtp import EmailService
from meter.main import create_app


# https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#configure-the-in-memory-database
def get_in_memory_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def get_test_config():
    return MeterConfig(
        sql=SQLEngineParam(
            url="sqlite://",
            connect_args={"check_same_thread": False},
        ),
        auth=AuthConfig(
            secret_key="i-am-example-secret-key",
            algorithm="HS256",
            default_ttl_sec=900,
        ),
        verify_email=VerifyEmailParam(
            subject="Hi", template_path="./templates/verify_mail.html", expire=60
        ),
        smtp=SMTPServerParam(
            server="msa.hinet.net",
            port=587,
            noreply="test@gmail.com",
            noreply_password=None,
        ),
        host="https://noj.tw",
    )


@pytest.fixture
def test_session():
    engine = get_in_memory_engine()
    create_db_and_tables(engine)
    with Session(engine) as session:
        yield session


def get_email_service_override():
    class NewEmailService(EmailService):
        def __init__(self, *args, **kargs) -> None:
            super(NewEmailService, self).__init__(*args, **kargs)

        def send(self, *args, **kargs):
            pass

    return NewEmailService(get_test_config().smtp)


@pytest.fixture
def test_app(tmp_path: Path, test_session: Session):
    def get_test_session():
        return test_session

    tmp_config_path = tmp_path / "meter.toml"
    toml.dump(get_test_config().dict(), tmp_config_path.open("w"))
    os.environ["METER_CONFIG"] = str(tmp_config_path.absolute())

    app = create_app()
    app.dependency_overrides[get_config] = get_test_config
    app.dependency_overrides[get_session] = get_test_session
    app.dependency_overrides[get_email_service] = get_email_service_override
    app.dependency_overrides[get_session] = get_test_session
    yield app
    app.dependency_overrides.clear()

    del os.environ["METER_CONFIG"]


@pytest.fixture
def test_client(test_app):
    with TestClient(test_app) as client:
        yield client
