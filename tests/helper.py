from fastapi.testclient import TestClient

from meter.domain.user import UserSignup


def register_and_login(test_client: TestClient, user: UserSignup):
    test_client.post(
        "/user/signup",
        json={
            "name": user.name,
            "email": user.email,
            "password": user.password,
        },
    )
    resp = test_client.post(
        "/auth/token",
        data={
            "username": user.name,
            "password": user.password
        },
    )
    return resp.json()


def get_authorization_header(test_client: TestClient, user: UserSignup):
    token = register_and_login(test_client, user)
    return {"Authorization": f'{token["token_type"]} {token["access_token"]}'}
