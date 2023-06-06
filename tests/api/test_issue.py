from fastapi import status
from fastapi.testclient import TestClient

from meter.constant.issue_status import IssueStatus
from meter.constant.rule_operator import RuleOperator
from meter.constant.rule_position import RulePosition
from meter.constant.rule_resource import RuleResource
from meter.domain.issue import IssueService
from meter.domain.user import UserSignup
from tests.helper import get_authorization_header


class TestIssueClass:
    def test_get_issues_unauthorized(self, test_client: TestClient):
        res = test_client.get("/issue")

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_issues(self, test_client: TestClient):
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
        test_client.put(
            "/rule/1/trigger",
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
                "operator": RuleOperator.GREATER_THAN,
                "value": 50,
            },
            headers=header,
        )
        test_client.put(
            "/rule/2/trigger",
            headers=header,
        )
        test_client.post(
            "/rule",
            json={
                "name": "foo2",
                "position": RulePosition.DEJI_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.LESS_THAN,
                "value": 60,
            },
            headers=header,
        )
        test_client.put(
            "/rule/3/trigger",
            headers=header,
        )

        res = test_client.get("/issue", headers=header)

        assert res.status_code == status.HTTP_200_OK
        for obj in res.json():
            assert list(obj.keys()) == [
                "id",
                "title",
                "status",
                "created_at",
                "updated_at",
            ]
        assert len(res.json()) == 2

        # test filter
        test_client.patch(
            f"/issue/2",
            json={
                "status": IssueStatus.SOLVED.value,
            },
            headers=header,
        )

        res = test_client.get(
            f"/issue?status={IssueStatus.SOLVED.value}", headers=header
        )
        assert len(res.json()) == 1

    def test_show_issue_unauthorized(self, test_client: TestClient):
        res = test_client.get(f"/issue/1")

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_show_issue(self, test_client: TestClient):
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
                "position": RulePosition.DEJI_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.LESS_THAN,
                "value": 50,
            },
            headers=header,
        )
        test_client.put(
            "/rule/1/trigger",
            headers=header,
        )

        res = test_client.get(f"/issue/1", headers=header)

        assert res.status_code == status.HTTP_200_OK
        assert list(res.json().keys()) == [
            "id",
            "title",
            "status",
            "created_at",
            "updated_at",
            "content",
            "processing_at",
            "solved_at",
            "rule",
        ]

    def test_show_others_issue(self, test_client: TestClient):
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
                "position": RulePosition.DEJI_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.LESS_THAN,
                "value": 0,
            },
            headers=header,
        )
        test_client.put(
            "/rule/1/trigger",
            headers=header,
        )

        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.get(f"/issue/1", headers=header)

        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_update_issue_unauthorized(self, test_client: TestClient):
        res = test_client.patch(f"/issue/1")

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_issue(self, test_client: TestClient):
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
                "position": RulePosition.DEJI_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.LESS_THAN,
                "value": 50,
            },
            headers=header,
        )
        test_client.put(
            "/rule/1/trigger",
            headers=header,
        )

        res = test_client.patch(
            f"/issue/1",
            json={
                "title": "new title",
                "content": "hey, I fixed it :)",
                "status": IssueStatus.SOLVED.value,
            },
            headers=header,
        )
        json = res.json()
        assert res.status_code == status.HTTP_200_OK
        assert json["status"] == IssueStatus.SOLVED.value
        assert json["title"] == "new title"
        assert json["content"] == "hey, I fixed it :)"

    def test_update_others_issue(self, test_client: TestClient):
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
                "position": RulePosition.DEJI_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.LESS_THAN,
                "value": 0,
            },
            headers=header,
        )
        test_client.put(
            "/rule/1/trigger",
            headers=header,
        )

        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.patch(
            f"/issue/1",
            json={},
            headers=header,
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_update_issue_failed(
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

        monkeypatch.setattr(IssueService, "update", mock_update)

        test_client.post(
            "/rule",
            json={
                "name": "foo",
                "position": RulePosition.DEJI_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.LESS_THAN,
                "value": 50,
            },
            headers=header,
        )
        test_client.put(
            "/rule/1/trigger",
            headers=header,
        )

        res = test_client.patch(
            f"/issue/1",
            json={},
            headers=header,
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_issue_unauthorized(self, test_client: TestClient):
        res = test_client.delete(f"/issue/1")

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_rule(self, test_client: TestClient):
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
                "position": RulePosition.DEJI_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.LESS_THAN,
                "value": 50,
            },
            headers=header,
        )
        test_client.put(
            "/rule/1/trigger",
            headers=header,
        )

        res = test_client.delete(f"/issue/1", headers=header)
        assert res.status_code == status.HTTP_204_NO_CONTENT

        res = test_client.get(f"/issue/1", headers=header)
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
                "position": RulePosition.DEJI_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.LESS_THAN,
                "value": 0,
            },
            headers=header,
        )
        test_client.put(
            "/rule/1/trigger",
            headers=header,
        )

        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        res = test_client.delete(f"/issue/1", headers=header)
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_issue_failed(self, monkeypatch, test_client: TestClient):
        def mock_delete():
            raise Exception

        user = UserSignup(
            name="foo",
            email="foo@foo.com",
            password="foo",
        )
        header = get_authorization_header(test_client, user)

        monkeypatch.setattr(IssueService, "delete", mock_delete)

        test_client.post(
            "/rule",
            json={
                "name": "foo",
                "position": RulePosition.DEJI_RESERVOIR,
                "resource": RuleResource.PERCENT,
                "operator": RuleOperator.LESS_THAN,
                "value": 50,
            },
            headers=header,
        )
        test_client.put(
            "/rule/1/trigger",
            headers=header,
        )

        res = test_client.delete(f"/issue/1", headers=header)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

        res = test_client.get(f"/issue/1", headers=header)
        assert res.status_code == status.HTTP_200_OK
