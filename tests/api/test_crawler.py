import json

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from crawler.model import Dam, Eq, Power


class TestCrawlerClass:
    def setup_method(self, test_session: Session) -> None:
        for c in (Power, Eq, Dam):
            report = json.load(open(f"crawler/example/{c.__name__.lower()}.json"))
            for r in report:
                test_session().add(c(**r))
                test_session().commit()

    def test_get_power(self, test_client: TestClient):
        # I don't know why it is not working
        resp = test_client.get("/crawler/power")
        assert resp.status_code == status.HTTP_200_OK, resp.json()
