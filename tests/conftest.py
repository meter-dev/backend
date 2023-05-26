import pytest
from fastapi.testclient import TestClient
from meter.main import app
from meter.api import get_session
from sqlmodel import create_engine, SQLModel, Session
from sqlmodel.pool import StaticPool


# https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#configure-the-in-memory-database
def get_in_memory_engine():
    return create_engine(
        'sqlite://',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )


@pytest.fixture
def test_session():
    engine = get_in_memory_engine()
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def test_client(test_session: Session):
    def get_session_override():
        return test_session

    app.dependency_overrides[get_session] = get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()
