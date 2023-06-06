import logging
from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, Session, SQLModel, select

from meter.constant.rule_operator import RuleOperator
from meter.constant.rule_position import RulePosition
from meter.constant.rule_resource import RuleResource
from meter.domain.user import User


class RuleBase(SQLModel):
    name: Optional[str] = Field(index=True)
    position: RulePosition = Field(index=True)
    resource: RuleResource = Field(index=True)
    operator: RuleOperator
    value: float
    is_enable: bool


class Rule(RuleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        index=True,
        foreign_key="user.id",
    )
    user: User = Relationship(back_populates="rules")
    issues: List["Issue"] = Relationship(back_populates="rule")
    last_triggered_by: Optional[datetime] = Field(default=None, nullable=True)


class CreateRule(SQLModel):
    name: Optional[str]
    position: RulePosition
    resource: RuleResource
    operator: RuleOperator
    value: float


class UpdateRule(SQLModel):
    name: Optional[str]
    position: Optional[RulePosition]
    resource: Optional[RuleResource]
    operator: Optional[RuleOperator]
    value: Optional[float]


class ReadRule(RuleBase):
    id: int


class RuleService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def __get_rule_by_id_and_user_id(
        self,
        id: int,
        userId: int,
    ) -> Rule | None:
        statement = select(Rule).where(Rule.id == id).where(Rule.user_id == userId)
        results = self.session.exec(statement)
        return results.first()

    def create(self, input: CreateRule, user: User) -> Rule:
        rule = Rule(
            user_id=user.id,
            name=input.name,
            position=input.position,
            resource=input.resource,
            operator=input.operator,
            value=input.value,
            is_enable=True,
        )
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
        statement = select(Rule).where(Rule.user_id == user.id)
        results = self.session.exec(statement)
        return results.all()

    def show(self, user: User, id: int) -> Rule | None:
        if user.id is None:
            return None

        return self.__get_rule_by_id_and_user_id(id, user.id)

    def update(self, id: int, input: UpdateRule, user: User) -> Rule | None:
        if user.id is None:
            return None

        rule = self.__get_rule_by_id_and_user_id(id, user.id)
        if rule is None:
            return None

        rule.name = input.name or rule.name
        rule.position = input.position or rule.position
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

    def delete(self, id: int, user: User) -> bool:
        if user.id is None:
            return False

        rule = self.__get_rule_by_id_and_user_id(id, user.id)
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
        if user.id is None:
            return False

        rule = self.__get_rule_by_id_and_user_id(id, user.id)
        if rule is None:
            return False

        rule.is_enable = True

        self.session.add(rule)
        try:
            self.session.commit()
        except Exception as e:
            logging.error(f"[enable_rule] failed: id = {id}, exception = {e}!")
            raise e

        return True

    def disable(self, id: int, user: User) -> bool:
        if user.id is None:
            return False

        rule = self.__get_rule_by_id_and_user_id(id, user.id)
        if rule is None:
            return False

        rule.is_enable = False

        self.session.add(rule)
        try:
            self.session.commit()
        except Exception as e:
            logging.error(f"[disable_rule] failed: id = {id}, exception = {e}!")
            raise e

        return True
