from typing import Optional
import logging

from meter.domain.user import User

from sqlmodel import Field, Session, SQLModel, select


class RuleBase(SQLModel):
    name: Optional[str] = Field(index=True)
    resource: str = Field(index=True)
    operator: str
    value: int
    is_enable: bool


class Rule(RuleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(index=True, default=None, foreign_key="user.id")


class CreateRule(RuleBase):
    pass


class UpdateRule(RuleBase):
    resource: Optional[str]
    operator: Optional[str]
    value: Optional[int]


class ReadRule(RuleBase):
    id: int


class RuleService:
    def __init__(self, session: Session) -> None:
        self.session = session

    # TODO: check user id after auth done.
    def __get_rule_by_id(self, id) -> Rule | None:
        statement = select(Rule).where(Rule.id == id)
        results = self.session.exec(statement)
        return results.first()

    def create(self, input: CreateRule, user: User) -> Rule | None:
        rule = Rule(
            user_id=1,  # TODO: change to `user.id` after auth done.
            name=input.name,
            resource=input.resource,
            operator=input.operator,
            value=input.value,
            is_enable=True,
        )
        print(rule)
        self.session.add(rule)

        try:
            self.session.commit()
        except Exception as e:
            logging.error(f"[create_rule] failed: input = {input}, exception = {e}!")
            self.session.rollback()
            raise e

        self.session.refresh(rule)
        return rule

    def get(self, user: User) -> list[Rule]:
        statement = select(Rule).where(
            Rule.user_id == 1  # TODO: change to `user.id` after auth done.
        )
        results = self.session.exec(statement)
        return results.all()

    def update(self, id: int, input: UpdateRule, user: User) -> Rule | None:
        rule = self.__get_rule_by_id(id)
        if rule is None:
            return None

        rule.name = input.name or rule.name
        rule.resource = input.resource or rule.resource
        rule.operator = input.operator or rule.operator
        rule.value = input.value or rule.value

        self.session.add(rule)
        try:
            self.session.commit()
        except Exception as e:
            logging.error(f"[update_rule] failed: id = {id}, exception = {e}!")
            raise e
        self.session.refresh(rule)

        return rule

    def delete(self, id: int) -> bool:
        rule = self.__get_rule_by_id(id)
        if rule is None:
            return False

        self.session.delete(rule)
        try:
            self.session.commit()
        except Exception as e:
            logging.error(f"[delete_rule] failed: id = {id}, exception = {e}!")
            raise e

        return True

    def enable(self, id: int, user: User) -> bool:
        rule = self.__get_rule_by_id(id)
        if rule is None:
            return False

        rule.is_enable = True

        self.session.add(rule)
        try:
            self.session.commit()
        except Exception as e:
            logging.error(f"[enable_rule] failed: id = {id}, exception = {e}!")
            raise e
        self.session.refresh(rule)

        return rule

    def disable(self, id: int, user: User) -> bool:
        rule = self.__get_rule_by_id(id)
        if rule is None:
            return False

        rule.is_enable = False

        self.session.add(rule)
        try:
            self.session.commit()
        except Exception as e:
            logging.error(f"[disable_rule] failed: id = {id}, exception = {e}!")
            raise e
        self.session.refresh(rule)

        return rule
