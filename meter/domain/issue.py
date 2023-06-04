import logging
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, Session, SQLModel, select

from meter.constant.issue_status import IssueStatus
from meter.constant.template_path import TemplatePath
from meter.domain.rule import Rule
from meter.domain.user import User
from meter.helper import get_formatted_string_from_template


class IssueBase(SQLModel):
    title: str = Field(index=True)
    content: str = Field()
    status: IssueStatus = Field(default=IssueStatus.CREATED, nullable=False, index=True)


class Issue(IssueBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(
        index=True,
        default=None,
        foreign_key="user.id",
    )

    rule_id: Optional[int] = Field(
        index=True,
        default=None,
        foreign_key="rule.id",
    )
    rule: Optional[Rule] = Relationship(back_populates="issues")

    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    processing_at: datetime = Field(default=None, nullable=True)
    solved_at: datetime = Field(default=None, nullable=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class CreateIssue(SQLModel):
    title: str
    content: str


class UpdateIssue(SQLModel):
    title: Optional[str]
    content: Optional[str]
    status: Optional[IssueStatus]


class ReadIssue(SQLModel):
    id: int
    title: str = Field(index=True)
    status: IssueStatus = Field(default=IssueStatus.CREATED, nullable=False, index=True)
    created_at: datetime
    updated_at: datetime


class ReadIssueDetail(ReadIssue):
    content: str
    processing_at: Optional[datetime]
    solved_at: Optional[datetime]
    rule: Rule


class IssueService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def __get_by_id_and_user_id(
        self,
        id: int,
        userId: int,
    ) -> Issue | None:
        statement = select(Issue).where(Issue.id == id).where(Issue.user_id == userId)
        results = self.session.exec(statement)
        return results.first()

    def create(self, rule: Rule) -> Issue:
        rule_name = rule.name or rule.id

        issue = Issue(
            user_id=rule.user_id,
            rule_id=rule.id,
            title=get_formatted_string_from_template(
                TemplatePath.ISSUE_TITLE.value,
                rule_name=rule_name,
            ),
            content=get_formatted_string_from_template(
                TemplatePath.ISSUE_CONTENT.value
            ),
            status=IssueStatus.CREATED.value,
        )
        self.session.add(issue)

        try:
            self.session.commit()
        except Exception as e:
            logging.error(f"[create_issue] failed: input = {input}, exception = {e}!")
            self.session.rollback()
            raise e

        self.session.refresh(issue)
        return issue

    def get(self, user: User, filter: dict) -> list[Issue]:
        statement = select(Issue).where(Issue.user_id == user.id)

        # filter
        for key, value in filter.items():
            if value is not None:
                statement = statement.where(getattr(Issue, key) == value)

        results = self.session.exec(statement)
        return results.all()

    def show(self, user: User, id: int) -> Issue | None:
        if user.id is None:
            return None
        return self.__get_by_id_and_user_id(id, user.id)

    def update(self, id: int, input: UpdateIssue, user: User) -> Issue | None:
        if user.id is None:
            return None

        issue = self.__get_by_id_and_user_id(id, user.id)
        if issue is None:
            return None

        issue.title = input.title or issue.title
        issue.content = input.content or issue.content
        issue.status = input.status or issue.status

        # update timestamp
        if input.status == IssueStatus.PROCESSING:
            issue.processing_at = datetime.utcnow()
        elif input.status == IssueStatus.SOLVED:
            issue.solved_at = datetime.utcnow()

        self.session.add(issue)
        try:
            self.session.commit()
        except Exception as e:
            logging.error(f"[update_issue] failed: id = {id}, exception = {e}!")
            raise e
        self.session.refresh(issue)

        return issue

    def delete(self, id: int, user: User) -> bool:
        if user.id is None:
            return False

        issue = self.__get_by_id_and_user_id(id, user.id)
        if issue is None:
            return False

        self.session.delete(issue)
        try:
            self.session.commit()
        except Exception as e:
            logging.error(f"[delete_issue] failed: id = {id}, exception = {e}!")
            raise e

        return True
