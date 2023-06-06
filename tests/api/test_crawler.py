import json

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from crawler.model import Dam, Eq, Power


class TestCrawlerClass:
    # TODO: make this auto-execute at the start of the testing
    def load_data(self, test_session: Session) -> None:
        for c in (Power, Eq, Dam):
            report = json.load(open(f"crawler/example/{c.__name__.lower()}.json"))
            for r in report:
                test_session.add(c(**r))
                test_session.commit()

    def test_get_power(self, test_client: TestClient, test_session: Session):
        self.load_data(test_session)

        resp = test_client.get("/crawler/power")
        assert resp.status_code == status.HTTP_200_OK, resp.json()
        id = resp.json()[0]["id"]

        resp = test_client.get(f"/crawler/power/{id}")
        assert resp.status_code == status.HTTP_200_OK, resp.json()

    def test_get_eq(self, test_client: TestClient, test_session: Session):
        self.load_data(test_session)

        resp = test_client.get("/crawler/eq")
        assert resp.status_code == status.HTTP_200_OK, resp.json()
        id = resp.json()[0]["id"]

        resp = test_client.get(f"/crawler/eq/{id}")
        assert resp.status_code == status.HTTP_200_OK, resp.json()

    def test_get_dam(self, test_client: TestClient, test_session: Session):
        self.load_data(test_session)

        resp = test_client.get("/crawler/dam")
        assert resp.status_code == status.HTTP_200_OK, resp.json()
        id = resp.json()[0]["id"]

        resp = test_client.get(f"/crawler/dam/{id}")
        assert resp.status_code == status.HTTP_200_OK, resp.json()
