import json

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from crawler.model import Dam, Eq, Power


class TestReportClass:
    @pytest.fixture(autouse=True)
    def setup_method(self, test_session: Session) -> None:
        for c in (Power, Eq, Dam):
            report = json.load(open(f"crawler/example/{c.__name__.lower()}.json"))
            for r in report:
                test_session.add(c(**r))
                test_session.commit()

    def test_get_power(self, test_client: TestClient):
        resp = test_client.get("/report/power")
        assert resp.status_code == status.HTTP_200_OK, resp.json()
        power = resp.json()[0]
        assert "whole" in power.keys(), resp.json()
        assert (
            power["whole"]["max_supply"]
            - sum(power[k]["max_supply"] for k in ("north", "central", "south"))
            < 0.01
        )
        assert (
            power["whole"]["load"]
            - sum(power[k]["load"] for k in ("north", "central", "south", "east"))
            < 0.01
        )

    def test_get_eq(self, test_client: TestClient):
        resp = test_client.get("/report/eq")
        assert resp.status_code == status.HTTP_200_OK, resp.json()

    def test_get_dam(self, test_client: TestClient):
        resp = test_client.get("/report/dam")
        assert resp.status_code == status.HTTP_200_OK, resp.json()
        assert any(filter(lambda d: d["name"] == "竹", resp.json())), resp.json()
