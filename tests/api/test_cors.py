from fastapi import status
from fastapi.testclient import TestClient

from meter.api.cors import CORSConfig, set_cors


def test_set_cors(test_app):
    set_cors(test_app, CORSConfig(allow_origins=["http://example.com"]))
    with TestClient(test_app) as client:
        resp = client.options(
            "/auth/token",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        resp = client.options(
            "/auth/token",
            headers={
                "Origin": "http://not-example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.headers["vary"] == "Origin", resp.headers
