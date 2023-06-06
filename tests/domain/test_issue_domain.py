from datetime import datetime

import pytest

from meter.constant.issue_status import IssueStatus
from meter.constant.template_path import TemplatePath
from meter.domain.issue import Issue, IssueService, UpdateIssue
from meter.domain.rule import Rule
from meter.domain.user import User
from meter.helper import get_formatted_string_from_template


class MockResult:
    def all(self):
        return []

    def first(self):
        return None


class MockSession:
    def exec(self, arg1):
        return MockResult()

    def add(self, arg1):
        pass

    def commit(self):
        pass

    def refresh(self, arg1):
        pass

    def rollback(self):
        pass

    def delete(self, arg1):
        pass


class TestIssueDomainClass:
    def setup_method(self) -> None:
        self.service = IssueService(MockSession())

    def test_create(self):
        rule = Rule(
            id=1,
            user_id=1,
            name="foo",
            position="Taipei",
            resource="foo",
            operator=">",
            value=12,
        )
        issue = self.service.create(rule)

        assert (
            issue.user_id == rule.user_id
            and issue.rule_id == rule.id
            and issue.title
            == get_formatted_string_from_template(
                TemplatePath.ISSUE_TITLE.value,
                rule_name="foo",
            )
            and issue.content
            == get_formatted_string_from_template(
                TemplatePath.ISSUE_CONTENT.value,
            )
            and issue.status.value == IssueStatus.CREATED.value
        )

    def test_create_failed(self, monkeypatch):
        def mock_commit(arg1):
            raise Exception()

        monkeypatch.setattr(MockSession, "commit", mock_commit)
        self.service = IssueService(MockSession())

        rule = Rule(
            id=1,
            user_id=1,
            name="foo",
            position="Taipei",
            resource="foo",
            operator=">",
            value=12,
        )
        with pytest.raises(Exception):
            self.service.create(rule)

    def test_get(self):
        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        rules = self.service.get(by_user, {})

        assert rules == []

    def test_show_no_user_id(self):
        by_user = User(
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        rules = self.service.show(by_user, 1)

        assert rules == None

    def test_show(self):
        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        rules = self.service.show(by_user, 1)

        assert rules == None

    def test_update_no_user_id(self):
        by_user = User(
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        resource = UpdateIssue(
            title="title",
            content="content",
            status=IssueStatus.PROCESSING,
        )
        rules = self.service.update(1, resource, by_user)

        assert rules == None

    def test_update_no_result(self):
        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        resource = UpdateIssue(
            title="title",
            content="content",
            status=IssueStatus.PROCESSING,
        )
        rules = self.service.update(1, resource, by_user)

        assert rules == None

    def test_update_failed(self, monkeypatch):
        def mock_commit(arg1):
            raise Exception()

        def mock_first(arg1):
            return Issue(
                id=1,
                user_id=1,
                rule_id=1,
                title="foo",
                content="ooo",
                status=IssueStatus.CREATED,
            )

        monkeypatch.setattr(MockSession, "commit", mock_commit)
        monkeypatch.setattr(MockResult, "first", mock_first)
        self.service = IssueService(MockSession())

        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )

        resource = UpdateIssue(
            title="title",
            content="content",
            status=IssueStatus.PROCESSING,
        )

        with pytest.raises(Exception):
            self.service.update(1, resource, by_user)

    def test_update(self, monkeypatch):
        now_time = datetime.utcnow()

        def mockGetIssue(arg1):
            return Issue(
                id=1,
                user_id=1,
                rule_id=1,
                title="foo",
                content="ooo",
                status=IssueStatus.CREATED,
                created_at=now_time,
                updated_at=now_time,
            )

        monkeypatch.setattr(MockResult, "first", mockGetIssue)
        self.service = IssueService(MockSession())

        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        resource = UpdateIssue(
            title="title",
            content="content",
            status=IssueStatus.PROCESSING,
        )

        issue = self.service.update(1, resource, by_user)
        assert issue is not None
        assert (
            issue.user_id == 1
            and issue.rule_id == 1
            and issue.title == "title"
            and issue.content == "content"
            and issue.status.value == IssueStatus.PROCESSING.value
            and issue.processing_at is not None
            and issue.created_at == now_time
            and issue.updated_at != now_time
        )

        # and try to update to solved
        resource = UpdateIssue(
            status=IssueStatus.SOLVED,
        )
        issue = self.service.update(1, resource, by_user)
        assert issue is not None
        assert (
            issue.status.value == IssueStatus.SOLVED.value
            and issue.solved_at is not None
        )

    def test_update_nothing(self, monkeypatch):
        now_time = datetime.utcnow()

        def mockGetIssue(arg1):
            return Issue(
                id=1,
                user_id=1,
                rule_id=1,
                title="foo",
                content="ooo",
                status=IssueStatus.CREATED,
                created_at=now_time,
                updated_at=now_time,
            )

        monkeypatch.setattr(MockResult, "first", mockGetIssue)
        self.service = IssueService(MockSession())

        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        resource = UpdateIssue(
            title=None,
            content=None,
            status=None,
        )

        issue = self.service.update(1, resource, by_user)
        assert issue is not None
        assert (
            issue.user_id == 1
            and issue.rule_id == 1
            and issue.title == "foo"
            and issue.content == "ooo"
            and issue.status.value == IssueStatus.CREATED.value
            and issue.created_at == now_time
            and issue.updated_at == now_time
        )

    def test_delete_no_user_id(self):
        by_user = User(
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        success = self.service.delete(1, by_user)

        assert success == False

    def test_delete_no_result(self):
        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        success = self.service.delete(1, by_user)

        assert success == False

    def test_delete_failed(self, monkeypatch):
        def mock_commit(arg1):
            raise Exception()

        def mock_first(arg1):
            return Rule(
                id=1,
                user_id=1,
                name="123",
                position="Taipei",
                resource="water",
                operator=">",
                value=50,
            )

        monkeypatch.setattr(MockSession, "commit", mock_commit)
        monkeypatch.setattr(MockResult, "first", mock_first)
        self.service = IssueService(MockSession())

        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )

        with pytest.raises(Exception):
            self.service.delete(1, by_user)

    def test_delete(self, monkeypatch):
        def mockGetRule(arg1):
            return Rule(
                id=1,
                user_id=1,
                name="1234",
                position="Taipei2",
                resource="water2",
                operator="=",
                value=60,
            )

        monkeypatch.setattr(MockResult, "first", mockGetRule)
        self.service = IssueService(MockSession())

        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )

        success = self.service.delete(1, by_user)
        assert success == True
