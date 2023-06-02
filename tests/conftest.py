import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from meter.api import get_config, get_email_service, get_session
from meter.config import MeterConfig
from meter.domain import SMTPServerParam, SQLEngineParam, VerifyEmailParam
from meter.domain.auth import AuthConfig
from meter.domain.smtp import EmailService
from meter.main import app


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
            subject="Hi",
            content="Verify here: https://noj.tw/auth/active?token={access_token}",
        ),
        smtp=SMTPServerParam(
            server="msa.hinet.net",
            noreply="test@gmail.com",
            noreply_password="",
        ),
    )


@pytest.fixture
def test_session():
    engine = get_in_memory_engine()
    SQLModel.metadata.create_all(engine)
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
def test_client(test_session: Session):
    def get_session_override():
        return test_session

    app.dependency_overrides[get_config] = get_test_config
    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_email_service] = get_email_service_override
    yield TestClient(app)
    app.dependency_overrides.clear()
