from fastapi import status
from fastapi.testclient import TestClient

from meter.domain.user import UserSignup
from tests.helper import get_authorization_header
from meter.constant.response_code import ResponseCode


def test_signup_and_login(test_client: TestClient):
    resp = test_client.post(
        "/user/signup",
        json={
            "name": "foo",
            "email": "foo@bar.com",
            "password": "foo",
        },
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.json()
    resp = test_client.post(
        "/auth/token",
        data={"username": "foo", "password": "foo"},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.json()
    token = resp.json()

    resp = test_client.get(
        "/me",
        headers={"Authorization": f'{token["token_type"]} {token["access_token"]}'},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.json()
    assert resp.json()["name"] == "foo", resp.json()

    resp = test_client.get(
        "/me", headers={"Authorization": f'{token["token_type"]} lol'}
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED, resp.json()


def test_signup_multiple_users(test_client: TestClient):
    inputs = [
        UserSignup(
            name="bar",
            email="bar@bar.com",
            password="foo",
        ),
        UserSignup(
            name="baz",
            email="baz@bar.com",
            password="foo",
        ),
    ]
    for i in inputs:
        resp = test_client.post(
            "/user/signup",
            json=i.dict(),
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.json()


def test_signup_wrong_password(test_client: TestClient):
    resp = test_client.post(
        "/user/signup",
        json={
            "name": "foo",
            "email": "foooooo",
            "password": "foo",
        },
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.json()
    assert resp.json()["detail"][0]["loc"][1] == "email", resp.json()


def test_signup_wrong_name(test_client: TestClient):
    resp = test_client.post(
        "/user/signup",
        json={
            "name": "台灣人",
            "email": "baz@bar.com",
            "password": "foo",
        },
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.json()
    assert resp.json()["detail"][0]["loc"][1] == "name", resp.json()

    resp = test_client.post(
        "/user/signup",
        json={
            "name": "a" * 33,
            "email": "baz@bar.com",
            "password": "foo",
        },
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.json()
    assert resp.json()["detail"][0]["loc"][1] == "name", resp.json()


def test_signup_duplicated(test_client: TestClient):
    resp = test_client.post(
        "/user/signup",
        json={
            "name": "Tai-uan-lang",
            "email": "baz@bar.com",
            "password": "foo",
        },
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.json()

    resp = test_client.post(
        "/user/signup",
        json={
            "name": "Tai-uan-lang",
            "email": "bak@bar.com",
            "password": "foo",
        },
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST, resp.json()
    assert resp.json()["code"] == ResponseCode.USER_SIGNUP_DUPLICATE_USERNAME_1301.value

    resp = test_client.post(
        "/user/signup",
        json={
            "name": "Tiong-kok-lang",
            "email": "baz@bar.com",
            "password": "foo",
        },
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST, resp.json()
    assert resp.json()["code"] == ResponseCode.USER_SIGNUP_DUPLICATE_EMAIL_1302.value


def test_login_by_email(test_client: TestClient):
    resp = test_client.post(
        "/user/signup",
        json={
            "name": "foo",
            "email": "foo@bar.com",
            "password": "foo",
        },
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.json()
    resp = test_client.post(
        "/auth/token",
        data={"username": "foo@bar.com", "password": "foo"},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.json()
    token = resp.json()
    resp = test_client.get(
        "/me",
        headers={"Authorization": f'{token["token_type"]} {token["access_token"]}'},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.json()
    assert resp.json()["name"] == "foo", resp.json()


def test_login_by_email_case_insensitive(test_client: TestClient):
    resp = test_client.post(
        "/user/signup",
        json={
            "name": "foo",
            "email": "foo@bar.com",
            "password": "foo",
        },
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.json()
    resp = test_client.post(
        "/auth/token",
        data={"username": "fOo@bAr.com", "password": "foo"},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.json()
    token = resp.json()
    resp = test_client.get(
        "/me",
        headers={"Authorization": f'{token["token_type"]} {token["access_token"]}'},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.json()
    assert resp.json()["name"] == "foo", resp.json()


def test_send_email_and_active(test_client: TestClient):
    user = UserSignup(
        name="foo",
        email="foo@google.com",
        password="foo",
    )
    headers = get_authorization_header(test_client, user)

    # Mock email server should not try to send anything while returning 200
    resp = test_client.post("/auth/send_email", headers=headers)
    assert resp.status_code == status.HTTP_200_OK, resp.json()
    token = resp.json()

    resp = test_client.get(f"/auth/active?token=lalala")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED, resp.json()

    resp = test_client.get(f"/auth/active?token={token}")
    assert resp.status_code == status.HTTP_204_NO_CONTENT, resp.json()

    resp = test_client.get(f"/auth/active?token={token}")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST, resp.json()

    resp = test_client.get("/me", headers=headers)
    assert resp.status_code == status.HTTP_200_OK, resp.json()
    assert resp.json()["active"] == True, resp.json()
