import pytest

from meter.constant.rule_operator import RuleOperator
from meter.constant.rule_position import RulePosition
from meter.constant.rule_resource import RuleResource
from meter.domain.rule import CreateRule, Rule, RuleService, UpdateRule
from meter.domain.user import User


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


class TestRuleDomainClass:
    def setup_method(self) -> None:
        self.service = RuleService(MockSession())

    def test_create(self):
        resource = CreateRule(
            name="foo",
            position=RulePosition.DEJI_RESERVOIR,
            resource=RuleResource.PERCENT,
            operator=RuleOperator.LESS_THAN,
            value=12,
        )
        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        rule = self.service.create(resource, by_user)

        assert rule == Rule(
            user_id=by_user.id,
            name=resource.name,
            position=resource.position,
            resource=resource.resource,
            operator=resource.operator,
            value=resource.value,
            is_enable=True,
        )

    def test_create_failed(self, monkeypatch):
        def mock_commit(arg1):
            raise Exception()

        monkeypatch.setattr(MockSession, "commit", mock_commit)
        self.service = RuleService(MockSession())

        resource = CreateRule(
            name="foo",
            position=RulePosition.DEJI_RESERVOIR,
            resource=RuleResource.PERCENT,
            operator=RuleOperator.LESS_THAN,
            value=12,
        )
        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        with pytest.raises(Exception):
            self.service.create(resource, by_user)

    def test_get(self):
        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        rules = self.service.get(by_user)

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
        resource = UpdateRule(
            name="123",
            position=RulePosition.DEJI_RESERVOIR,
            resource=RuleResource.PERCENT,
            operator=RuleOperator.LESS_THAN,
            value=50,
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
        resource = UpdateRule(
            name="123",
            position=RulePosition.DEJI_RESERVOIR,
            resource=RuleResource.PERCENT,
            operator=RuleOperator.LESS_THAN,
            value=50,
        )
        rules = self.service.update(1, resource, by_user)

        assert rules == None

    def test_update_failed(self, monkeypatch):
        def mock_commit(arg1):
            raise Exception()

        def mock_first(arg1):
            return Rule(
                id=1,
                user_id=1,
                name="123",
                position=RulePosition.DEJI_RESERVOIR,
                resource=RuleResource.PERCENT,
                operator=RuleOperator.LESS_THAN,
                value=50,
            )

        monkeypatch.setattr(MockSession, "commit", mock_commit)
        monkeypatch.setattr(MockResult, "first", mock_first)
        self.service = RuleService(MockSession())

        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        resource = UpdateRule(
            name="123",
            position=RulePosition.DEJI_RESERVOIR,
            resource=RuleResource.PERCENT,
            operator=RuleOperator.LESS_THAN,
            value=50,
        )

        with pytest.raises(Exception):
            self.service.update(1, resource, by_user)

    def test_update(self, monkeypatch):
        def mockGetRule(arg1):
            return Rule(
                id=1,
                user_id=1,
                name="1234",
                position=RulePosition.DEJI_RESERVOIR,
                resource=RuleResource.PERCENT,
                operator=RuleOperator.LESS_THAN,
                value=60,
            )

        monkeypatch.setattr(MockResult, "first", mockGetRule)
        self.service = RuleService(MockSession())

        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        resource = UpdateRule(
            name="123",
            position=RulePosition.AGONGDIAN_RESERVOIR,
            resource=RuleResource.STORAGE,
            operator=RuleOperator.GREATER_THAN,
            value=50,
        )

        rule = self.service.update(1, resource, by_user)
        assert rule == Rule(
            id=1,
            user_id=by_user.id,
            name="123",
            position=RulePosition.AGONGDIAN_RESERVOIR,
            resource=RuleResource.STORAGE,
            operator=RuleOperator.GREATER_THAN,
            value=50,
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
                position=RulePosition.DEJI_RESERVOIR,
                resource=RuleResource.PERCENT,
                operator=RuleOperator.LESS_THAN,
                value=50,
            )

        monkeypatch.setattr(MockSession, "commit", mock_commit)
        monkeypatch.setattr(MockResult, "first", mock_first)
        self.service = RuleService(MockSession())

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
                position=RulePosition.DEJI_RESERVOIR,
                resource=RuleResource.PERCENT,
                operator=RuleOperator.LESS_THAN,
                value=60,
            )

        monkeypatch.setattr(MockResult, "first", mockGetRule)
        self.service = RuleService(MockSession())

        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )

        success = self.service.delete(1, by_user)
        assert success == True

    def test_enable_no_user_id(self):
        by_user = User(
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        success = self.service.enable(1, by_user)

        assert success == False

    def test_enable_no_result(self):
        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        success = self.service.enable(1, by_user)

        assert success == False

    def test_enable_failed(self, monkeypatch):
        def mock_commit(arg1):
            raise Exception()

        def mock_first(arg1):
            return Rule(
                id=1,
                user_id=1,
                name="123",
                position=RulePosition.DEJI_RESERVOIR,
                resource=RuleResource.PERCENT,
                operator=RuleOperator.LESS_THAN,
                value=50,
            )

        monkeypatch.setattr(MockSession, "commit", mock_commit)
        monkeypatch.setattr(MockResult, "first", mock_first)
        self.service = RuleService(MockSession())

        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )

        with pytest.raises(Exception):
            self.service.enable(1, by_user)

    def test_enable(self, monkeypatch):
        def mockGetRule(arg1):
            return Rule(
                id=1,
                user_id=1,
                name="1234",
                position=RulePosition.DEJI_RESERVOIR,
                resource=RuleResource.PERCENT,
                operator=RuleOperator.LESS_THAN,
                value=60,
            )

        monkeypatch.setattr(MockResult, "first", mockGetRule)
        self.service = RuleService(MockSession())

        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )

        success = self.service.enable(1, by_user)
        assert success == True

    def test_disable_no_user_id(self):
        by_user = User(
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        success = self.service.disable(1, by_user)

        assert success == False

    def test_disable_no_result(self):
        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )
        success = self.service.disable(1, by_user)

        assert success == False

    def test_disable_failed(self, monkeypatch):
        def mock_commit(arg1):
            raise Exception()

        def mock_first(arg1):
            return Rule(
                id=1,
                user_id=1,
                name="123",
                position=RulePosition.DEJI_RESERVOIR,
                resource=RuleResource.PERCENT,
                operator=RuleOperator.LESS_THAN,
                value=50,
            )

        monkeypatch.setattr(MockSession, "commit", mock_commit)
        monkeypatch.setattr(MockResult, "first", mock_first)
        self.service = RuleService(MockSession())

        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )

        with pytest.raises(Exception):
            self.service.disable(1, by_user)

    def test_disable(self, monkeypatch):
        def mockGetRule(arg1):
            return Rule(
                id=1,
                user_id=1,
                name="1234",
                position=RulePosition.DEJI_RESERVOIR,
                resource=RuleResource.PERCENT,
                operator=RuleOperator.LESS_THAN,
                value=60,
            )

        monkeypatch.setattr(MockResult, "first", mockGetRule)
        self.service = RuleService(MockSession())

        by_user = User(
            id=1,
            name="foo",
            email="foo@foo.com",
            password_digest="somefakedigest",
        )

        success = self.service.disable(1, by_user)
        assert success == True
