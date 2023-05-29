import pytest

from meter.domain.rule import RuleService, Rule, CreateRule, UpdateRule
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
        resource = CreateRule(name='foo',
                              position='Taipei',
                              resource='foo',
                              operator='>',
                              value=12)
        byUser = User(
            id=1,
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )
        rule = self.service.create(resource, byUser)

        assert rule == Rule(
            user_id=byUser.id,
            name=resource.name,
            position=resource.position,
            resource=resource.resource,
            operator=resource.operator,
            value=resource.value,
            is_enable=True,
        )

    def test_create_failed(self, monkeypatch):

        def mockReturn(arg1):
            raise Exception()

        monkeypatch.setattr(MockSession, "commit", mockReturn)
        self.service = RuleService(MockSession())

        resource = CreateRule(name='foo',
                              position='Taipei',
                              resource='foo',
                              operator='>',
                              value=12)
        byUser = User(
            id=1,
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )
        with pytest.raises(Exception):
            self.service.create(resource, byUser)

    def test_get(self):
        byUser = User(
            id=1,
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )
        rules = self.service.get(byUser)

        assert rules == []

    def test_show_no_user_id(self):
        byUser = User(
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )
        rules = self.service.show(byUser, 1)

        assert rules == None

    def test_show(self):
        byUser = User(
            id=1,
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )
        rules = self.service.show(byUser, 1)

        assert rules == None

    def test_update_no_user_id(self):
        byUser = User(
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )
        resource = UpdateRule(name='123',
                              position='Taipei',
                              resource='water',
                              operator='>',
                              value=50)
        rules = self.service.update(1, resource, byUser)

        assert rules == None

    def test_update_no_result(self):
        byUser = User(
            id=1,
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )
        resource = UpdateRule(name='123',
                              position='Taipei',
                              resource='water',
                              operator='>',
                              value=50)
        rules = self.service.update(1, resource, byUser)

        assert rules == None

    def test_update_failed(self, monkeypatch):

        def mockReturn(arg1):
            raise Exception()

        def mockGetRule(arg1):
            return Rule(id=1,
                        user_id=1,
                        name='123',
                        position='Taipei',
                        resource='water',
                        operator='>',
                        value=50)

        monkeypatch.setattr(MockSession, "commit", mockReturn)
        monkeypatch.setattr(MockResult, "first", mockGetRule)
        self.service = RuleService(MockSession())

        byUser = User(
            id=1,
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )
        resource = UpdateRule(name='123',
                              position='Taipei',
                              resource='water',
                              operator='>',
                              value=50)

        with pytest.raises(Exception):
            self.service.update(1, resource, byUser)

    def test_update(self, monkeypatch):

        def mockGetRule(arg1):
            return Rule(id=1,
                        user_id=1,
                        name='1234',
                        position='Taipei2',
                        resource='water2',
                        operator='=',
                        value=60)

        monkeypatch.setattr(MockResult, "first", mockGetRule)
        self.service = RuleService(MockSession())

        byUser = User(
            id=1,
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )
        resource = UpdateRule(name='123',
                              position='Taipei',
                              resource='water',
                              operator='>',
                              value=50)

        rule = self.service.update(1, resource, byUser)
        assert rule == Rule(id=1,
                            user_id=byUser.id,
                            name='123',
                            position='Taipei',
                            resource='water',
                            operator='>',
                            value=50)

    def test_delete_no_user_id(self):
        byUser = User(
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )
        success = self.service.delete(1, byUser)

        assert success == False

    def test_delete_no_result(self):
        byUser = User(
            id=1,
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )
        success = self.service.delete(1, byUser)

        assert success == False

    def test_delete_failed(self, monkeypatch):

        def mockReturn(arg1):
            raise Exception()

        def mockGetRule(arg1):
            return Rule(id=1,
                        user_id=1,
                        name='123',
                        position='Taipei',
                        resource='water',
                        operator='>',
                        value=50)

        monkeypatch.setattr(MockSession, "commit", mockReturn)
        monkeypatch.setattr(MockResult, "first", mockGetRule)
        self.service = RuleService(MockSession())

        byUser = User(
            id=1,
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )

        with pytest.raises(Exception):
            self.service.delete(1, byUser)

    def test_delete(self, monkeypatch):

        def mockGetRule(arg1):
            return Rule(id=1,
                        user_id=1,
                        name='1234',
                        position='Taipei2',
                        resource='water2',
                        operator='=',
                        value=60)

        monkeypatch.setattr(MockResult, "first", mockGetRule)
        self.service = RuleService(MockSession())

        byUser = User(
            id=1,
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )

        success = self.service.delete(1, byUser)
        assert success == True

    def test_enable_no_user_id(self):
        byUser = User(
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )
        success = self.service.enable(1, byUser)

        assert success == False

    def test_enable_no_result(self):
        byUser = User(
            id=1,
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )
        success = self.service.enable(1, byUser)

        assert success == False

    def test_enable_failed(self, monkeypatch):

        def mockReturn(arg1):
            raise Exception()

        def mockGetRule(arg1):
            return Rule(id=1,
                        user_id=1,
                        name='123',
                        position='Taipei',
                        resource='water',
                        operator='>',
                        value=50)

        monkeypatch.setattr(MockSession, "commit", mockReturn)
        monkeypatch.setattr(MockResult, "first", mockGetRule)
        self.service = RuleService(MockSession())

        byUser = User(
            id=1,
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )

        with pytest.raises(Exception):
            self.service.enable(1, byUser)

    def test_enable(self, monkeypatch):

        def mockGetRule(arg1):
            return Rule(id=1,
                        user_id=1,
                        name='1234',
                        position='Taipei2',
                        resource='water2',
                        operator='=',
                        value=60)

        monkeypatch.setattr(MockResult, "first", mockGetRule)
        self.service = RuleService(MockSession())

        byUser = User(
            id=1,
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )

        success = self.service.enable(1, byUser)
        assert success == True

    def test_disable_no_user_id(self):
        byUser = User(
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )
        success = self.service.disable(1, byUser)

        assert success == False

    def test_disable_no_result(self):
        byUser = User(
            id=1,
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )
        success = self.service.disable(1, byUser)

        assert success == False

    def test_disable_failed(self, monkeypatch):

        def mockReturn(arg1):
            raise Exception()

        def mockGetRule(arg1):
            return Rule(id=1,
                        user_id=1,
                        name='123',
                        position='Taipei',
                        resource='water',
                        operator='>',
                        value=50)

        monkeypatch.setattr(MockSession, "commit", mockReturn)
        monkeypatch.setattr(MockResult, "first", mockGetRule)
        self.service = RuleService(MockSession())

        byUser = User(
            id=1,
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )

        with pytest.raises(Exception):
            self.service.disable(1, byUser)

    def test_disable(self, monkeypatch):

        def mockGetRule(arg1):
            return Rule(id=1,
                        user_id=1,
                        name='1234',
                        position='Taipei2',
                        resource='water2',
                        operator='=',
                        value=60)

        monkeypatch.setattr(MockResult, "first", mockGetRule)
        self.service = RuleService(MockSession())

        byUser = User(
            id=1,
            name='foo',
            email='foo@foo.com',
            password_digest='somefakedigest',
        )

        success = self.service.disable(1, byUser)
        assert success == True