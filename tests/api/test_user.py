from fastapi import status
from fastapi.testclient import TestClient


def test_signup_and_login(test_client: TestClient):
    resp = test_client.post(
        '/user/signup',
        json={
            'name': 'foo',
            'email': 'foo@bar.com',
            'password': 'foo',
        },
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.json()
    resp = test_client.post(
        '/auth/token',
        data={
            'username': 'foo',
            'password': 'foo'
        },
    )
    assert resp.status_code == status.HTTP_200_OK, resp.json()
