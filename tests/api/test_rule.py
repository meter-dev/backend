from fastapi import status
from fastapi.testclient import TestClient

from meter.constant.rule_operator import RuleOperator
from meter.constant.rule_position import RulePosition
from meter.constant.rule_resource import RuleResource
from meter.domain.issue import IssueService
from meter.domain.rule import RuleService
from meter.domain.user import UserSignup
from tests.helper import get_authorization_header


class TestRuleClass:
    def test_create_rule_unauthorized(self, test_client: TestClient):
        res = test_client.post("/rule")

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_rule(self, test_client: TestClient):
        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.post(
            "/rule",
            json={
                "name": "foo",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.EQUAL_TO,
                "value": 50,
            },
            headers=header,
        )

        assert res.status_code == status.HTTP_201_CREATED
        assert res.json() == {
            "name": "foo",
            "position": RulePosition.AGONGDIAN_RESERVOIR,
            "resource": RuleResource.PERCENT,
            "operator": RuleOperator.EQUAL_TO,
            "value": 50,
            "is_enable": True,
            "id": 1,
        }

    def test_create_rule_failed(self, test_client: TestClient, monkeypatch):
        def mock_create(arg1, arg2, arg3):
            raise Exception

        monkeypatch.setattr(RuleService, "create", mock_create)

        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.post(
            "/rule",
            json={
                "name": "foo",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.EQUAL_TO,
                "value": 50,
            },
            headers=header,
        )

        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_rules_unauthorized(self, test_client: TestClient):
        res = test_client.get("/rule")

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_rules(self, test_client: TestClient):
        # create a resource that should not be seen
        user = UserSignup(
            name="foo1",
            email="foo1@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)
        test_client.post(
            "/rule",
            json={
                "name": "foo2",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.EQUAL_TO,
                "value": 0,
            },
            headers=header,
        )

        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        test_client.post(
            "/rule",
            json={
                "name": "foo",
                "position": RulePosition.BAIHE_RESERVOIR,
                "resource": RuleResource.STORAGE,
                "operator": RuleOperator.EQUAL_TO,
                "value": 50,
            },
            headers=header,
        )
        test_client.post(
            "/rule",
            json={
                "name": "foo2",
                "position": RulePosition.DEJI_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.GREATER_THAN,
                "value": 60,
            },
            headers=header,
        )

        res = test_client.get("/rule", headers=header)

        assert res.status_code == status.HTTP_200_OK
        assert res.json() == [
            {
                "name": "foo",
                "position": RulePosition.BAIHE_RESERVOIR,
                "resource": RuleResource.STORAGE,
                "operator": RuleOperator.EQUAL_TO,
                "value": 50,
                "is_enable": True,
                "id": 2,
            },
            {
                "name": "foo2",
                "position": RulePosition.DEJI_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.GREATER_THAN,
                "value": 60,
                "is_enable": True,
                "id": 3,
            },
        ]

    def test_get_rule_unauthorized(self, test_client: TestClient):
        res = test_client.get(f"/rule/1")

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_rule(self, test_client: TestClient):
        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.post(
            "/rule",
            json={
                "name": "foo",
                "position": RulePosition.DEJI_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.GREATER_THAN,
                "value": 50,
            },
            headers=header,
        )
        json = res.json()

        res = test_client.get(f"/rule/{json['id']}", headers=header)

        assert res.status_code == status.HTTP_200_OK
        assert res.json() == {
            "name": "foo",
            "position": RulePosition.DEJI_RESERVOIR,
            "resource": RuleResource.PERCENT,
            "operator": RuleOperator.GREATER_THAN,
            "value": 50,
            "is_enable": True,
            "id": json["id"],
        }

    def test_get_others_rule(self, test_client: TestClient):
        # create a resource that should not be seen
        user = UserSignup(
            name="foo1",
            email="foo1@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)
        res = test_client.post(
            "/rule",
            json={
                "name": "foo2",
                "position": RulePosition.DEJI_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.GREATER_THAN,
                "value": 0,
            },
            headers=header,
        )
        json = res.json()

        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.get(f"/rule/{json['id']}", headers=header)

        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_update_rule_unauthorized(self, test_client: TestClient):
        res = test_client.patch(f"/rule/1")

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_rule(self, test_client: TestClient):
        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.post(
            "/rule",
            json={
                "name": "foo",
                "position": RulePosition.DEJI_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.GREATER_THAN,
                "value": 50,
            },
            headers=header,
        )
        json = res.json()

        res = test_client.patch(
            f"/rule/{json['id']}",
            json={
                "name": "foo2",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.STORAGE,
                "operator": RuleOperator.LESS_THAN,
                "value": 60,
            },
            headers=header,
        )
        assert res.status_code == status.HTTP_200_OK
        assert res.json() == {
            "name": "foo2",
            "position": RulePosition.AGONGDIAN_RESERVOIR,
            "resource": RuleResource.STORAGE,
            "operator": RuleOperator.LESS_THAN,
            "value": 60,
            "is_enable": True,
            "id": json["id"],
        }

    def test_update_others_rule(self, test_client: TestClient):
        user = UserSignup(
            name="foo1",
            email="foo1@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)
        res = test_client.post(
            "/rule",
            json={
                "name": "foo2",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.STORAGE,
                "operator": RuleOperator.LESS_THAN,
                "value": 0,
            },
            headers=header,
        )
        json = res.json()

        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.patch(
            f"/rule/{json['id']}",
            json={
                "name": "foo2",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.STORAGE,
                "operator": RuleOperator.LESS_THAN,
                "value": 60,
            },
            headers=header,
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_update_rule_failed(
        self,
        monkeypatch,
        test_client: TestClient,
    ):
        def mock_update():
            raise Exception

        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        monkeypatch.setattr(RuleService, "update", mock_update)

        res = test_client.patch(
            f"/rule/1",
            json={
                "name": "foo2",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.STORAGE,
                "operator": RuleOperator.LESS_THAN,
                "value": 60,
            },
            headers=header,
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_rule_unauthorized(self, test_client: TestClient):
        res = test_client.delete(f"/rule/1")

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_rule(self, test_client: TestClient):
        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.post(
            "/rule",
            json={
                "name": "foo",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.STORAGE,
                "operator": RuleOperator.LESS_THAN,
                "value": 50,
            },
            headers=header,
        )
        json = res.json()

        res = test_client.delete(f"/rule/{json['id']}", headers=header)
        assert res.status_code == status.HTTP_204_NO_CONTENT

        res = test_client.get(f"/rule/{json['id']}", headers=header)
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_others_rule(self, test_client: TestClient):
        user = UserSignup(
            name="foo1",
            email="foo1@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)
        res = test_client.post(
            "/rule",
            json={
                "name": "foo2",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.STORAGE,
                "operator": RuleOperator.LESS_THAN,
                "value": 0,
            },
            headers=header,
        )
        json = res.json()

        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.delete(f"/rule/{json['id']}", headers=header)
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_rule_failed(self, monkeypatch, test_client: TestClient):
        def mock_delete():
            raise Exception

        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        monkeypatch.setattr(RuleService, "delete", mock_delete)

        res = test_client.post(
            "/rule",
            json={
                "name": "foo",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.STORAGE,
                "operator": RuleOperator.LESS_THAN,
                "value": 50,
            },
            headers=header,
        )
        json = res.json()
        id = json["id"]

        res = test_client.delete(f"/rule/{id}", headers=header)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

        res = test_client.get(f"/rule/{id}", headers=header)
        assert res.status_code == status.HTTP_200_OK

    def test_enable_rule_unauthorized(self, test_client: TestClient):
        res = test_client.put(f"/rule/1/enable")

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_enable_rule(self, test_client: TestClient):
        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.post(
            "/rule",
            json={
                "name": "foo",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.STORAGE,
                "operator": RuleOperator.LESS_THAN,
                "value": 50,
            },
            headers=header,
        )
        json = res.json()
        id = json["id"]

        test_client.put(f"/rule/{id}/disable", headers=header)
        res = test_client.put(f"/rule/{id}/enable", headers=header)
        assert res.status_code == status.HTTP_204_NO_CONTENT

        res = test_client.get(f"/rule/{id}", headers=header)
        assert res.json()["is_enable"] == True

    def test_enable_others_rule(self, test_client: TestClient):
        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.post(
            "/rule",
            json={
                "name": "foo",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.STORAGE,
                "operator": RuleOperator.LESS_THAN,
                "value": 50,
            },
            headers=header,
        )
        json = res.json()
        id = json["id"]

        user = UserSignup(
            name="foo2",
            email="foo2@foo.com",
            password="foo2",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.put(f"/rule/{id}/enable", headers=header)
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_enable_rule_failed(self, monkeypatch, test_client: TestClient):
        def mock_enable():
            raise Exception

        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        monkeypatch.setattr(RuleService, "enable", mock_enable)

        res = test_client.put(f"/rule/1/enable", headers=header)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_disable_rule_unauthorized(self, test_client: TestClient):
        res = test_client.put(f"/rule/1/disable")

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_disable_rule(self, test_client: TestClient):
        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.post(
            "/rule",
            json={
                "name": "foo",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.STORAGE,
                "operator": RuleOperator.LESS_THAN,
                "value": 50,
            },
            headers=header,
        )
        json = res.json()
        id = json["id"]

        res = test_client.put(f"/rule/{id}/disable", headers=header)
        assert res.status_code == status.HTTP_204_NO_CONTENT

        res = test_client.get(f"/rule/{id}", headers=header)
        assert res.json()["is_enable"] == False

    def test_disable_others_rule(self, test_client: TestClient):
        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.post(
            "/rule",
            json={
                "name": "foo",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.STORAGE,
                "operator": RuleOperator.LESS_THAN,
                "value": 50,
            },
            headers=header,
        )
        json = res.json()
        id = json["id"]

        user = UserSignup(
            name="foo2",
            email="foo2@foo.com",
            password="foo2",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.put(f"/rule/{id}/disable", headers=header)
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_disable_rule_failed(self, monkeypatch, test_client: TestClient):
        def mock_disable():
            raise Exception

        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        monkeypatch.setattr(RuleService, "disable", mock_disable)

        res = test_client.put(f"/rule/1/disable", headers=header)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_trigger_rule_unauthorized(self, test_client: TestClient):
        res = test_client.put(f"/rule/1/trigger")

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_trigger_rule(self, test_client: TestClient):
        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.post(
            "/rule",
            json={
                "name": "foo",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.STORAGE,
                "operator": RuleOperator.LESS_THAN,
                "value": 50,
            },
            headers=header,
        )
        json = res.json()
        id = json["id"]

        res = test_client.put(f"/rule/{id}/trigger", headers=header)
        assert res.status_code == status.HTTP_204_NO_CONTENT

        res = test_client.get("/issue", headers=header)
        assert len(res.json()) == 1

    def test_trigger_others_rule(self, test_client: TestClient):
        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.post(
            "/rule",
            json={
                "name": "foo",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.STORAGE,
                "operator": RuleOperator.LESS_THAN,
                "value": 50,
            },
            headers=header,
        )
        json = res.json()
        id = json["id"]

        user = UserSignup(
            name="foo2",
            email="foo2@foo.com",
            password="foo2",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.put(f"/rule/{id}/trigger", headers=header)

        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_trigger_rule_failed(self, monkeypatch, test_client: TestClient):
        def mock_create():
            raise Exception

        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        monkeypatch.setattr(IssueService, "create", mock_create)

        test_client.post(
            "/rule",
            json={
                "name": "foo",
                "position": RulePosition.AGONGDIAN_RESERVOIR,
                "resource": RuleResource.STORAGE,
                "operator": RuleOperator.LESS_THAN,
                "value": 50,
            },
            headers=header,
        )

        res = test_client.put(f"/rule/1/trigger", headers=header)
        assert res.status_code == status.HTTP_400_BAD_REQUEST
