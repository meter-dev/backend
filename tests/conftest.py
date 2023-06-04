import os
from pathlib import Path

import pytest
import toml
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from meter.api import get_config, get_session
from meter.config import MeterConfig
from meter.domain import SQLEngineParam, create_db_and_tables
from meter.domain.auth import AuthConfig
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
    )


@pytest.fixture
def test_session():
    engine = get_in_memory_engine()
    create_db_and_tables(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def test_app(tmp_path: Path, test_session: Session):
    def get_test_session():
        return test_session

    tmp_config_path = tmp_path / "meter.toml"
    toml.dump(get_test_config().dict(), tmp_config_path.open("w"))
    os.environ["METER_CONFIG"] = str(tmp_config_path.absolute())

    app = create_app()
    app.dependency_overrides[get_session] = get_test_session
    yield app
    app.dependency_overrides.clear()

    del os.environ["METER_CONFIG"]


@pytest.fixture
def test_client(test_app):
    with TestClient(test_app) as client:
        yield client
