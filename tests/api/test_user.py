from fastapi import status
from fastapi.testclient import TestClient

from meter.domain.user import UserSignup


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


def test_signup_multiple_users(test_client: TestClient):
    inputs = [
        UserSignup(
            name='bar',
            email='bar@bar.com',
            password='foo',
        ),
        UserSignup(
            name='baz',
            email='baz@bar.com',
            password='foo',
        )
    ]
    for i in inputs:
        resp = test_client.post(
            '/user/signup',
            json=i.dict(),
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.json()


def test_signup_wrong_password(test_client: TestClient):
    resp = test_client.post(
        '/user/signup',
        json={
            'name': 'foo',
            'email': 'foooooo',
            'password': 'foo',
        },
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.json(
    )


def test_signup_wrong_name(test_client: TestClient):
    resp = test_client.post(
        '/user/signup',
        json={
            'name': '台灣人',
            'email': 'baz@bar.com',
            'password': 'foo',
        },
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.json(
    )

    resp = test_client.post(
        '/user/signup',
        json={
            'name': 'a' * 33,
            'email': 'baz@bar.com',
            'password': 'foo',
        },
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.json(
    )


def test_signup_duplicated(test_client: TestClient):
    resp = test_client.post(
        '/user/signup',
        json={
            'name': 'Tai-uan-lang',
            'email': 'baz@bar.com',
            'password': 'foo',
        },
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.json()

    resp = test_client.post(
        '/user/signup',
        json={
            'name': 'Tai-uan-lang',
            'email': 'bak@bar.com',
            'password': 'foo',
        },
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.json(
    )

    resp = test_client.post(
        '/user/signup',
        json={
            'name': 'Tiong-kok-lang',
            'email': 'baz@bar.com',
            'password': 'foo',
        },
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.json(
    )
