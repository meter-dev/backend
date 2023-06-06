from typing import Annotated

from fastapi import APIRouter, Depends, status

from meter.api import (
    get_current_user,
    get_email_service,
    get_issue_service,
    get_rule_service,
)
from meter.constant.response_code import ResponseCode
from meter.constant.template_path import TemplatePath
from meter.domain.issue import IssueService
from meter.domain.rule import CreateRule, ReadRule, RuleService, UpdateRule
from meter.domain.smtp import EmailService
from meter.domain.user import User
from meter.helper import (
    get_formatted_string_from_template,
    raise_custom_exception,
    raise_not_found_exception,
)

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ReadRule,
)
async def create_rule(
    svc: Annotated[RuleService, Depends(get_rule_service)],
    user: Annotated[User, Depends(get_current_user)],
    input: CreateRule,
):
    try:
        return svc.create(input, user)
    except Exception:
        raise_custom_exception(ResponseCode.RULE_CREATE_FAILED_1001)


# TODO: pagination
@router.get(
    "/",
    response_model=list[ReadRule],
)
async def get_rules(
    svc: Annotated[RuleService, Depends(get_rule_service)],
    user: Annotated[User, Depends(get_current_user)],
):
    return svc.get(user)


@router.get(
    "/{id}",
    response_model=ReadRule,
)
async def show_rule(
    svc: Annotated[RuleService, Depends(get_rule_service)],
    user: Annotated[User, Depends(get_current_user)],
    id: int,
):
    rule = svc.show(user, id)
    if rule is None:
        raise_not_found_exception()

    return rule


@router.patch(
    "/{id}",
    response_model=ReadRule,
)
async def update_rule(
    svc: Annotated[RuleService, Depends(get_rule_service)],
    user: Annotated[User, Depends(get_current_user)],
    id: int,
    input: UpdateRule,
):
    rule = None

    try:
        rule = svc.update(id, input, user)
    except Exception:
        raise_custom_exception(ResponseCode.RULE_UPDATE_FAILED_1002)

    if rule is None:
        raise_not_found_exception()

    return rule


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    svc: Annotated[RuleService, Depends(get_rule_service)],
    user: Annotated[User, Depends(get_current_user)],
    id: int,
):
    success = False

    try:
        success = svc.delete(id, user)
    except Exception:
        raise_custom_exception(ResponseCode.RULE_DELETE_FAILED_1003)

    if not success:
        raise_not_found_exception()


@router.put("/{id}/enable", status_code=status.HTTP_204_NO_CONTENT)
async def enable_rule(
    svc: Annotated[RuleService, Depends(get_rule_service)],
    user: Annotated[User, Depends(get_current_user)],
    id: int,
):
    success = False

    try:
        success = svc.enable(id, user)
    except Exception:
        raise_custom_exception(ResponseCode.RULE_ENABLE_FAILED_1004)

    if not success:
        raise_not_found_exception()


@router.put("/{id}/disable", status_code=status.HTTP_204_NO_CONTENT)
async def disable_rule(
    svc: Annotated[RuleService, Depends(get_rule_service)],
    user: Annotated[User, Depends(get_current_user)],
    id: int,
):
    success = False

    try:
        success = svc.disable(id, user)
    except Exception:
        raise_custom_exception(ResponseCode.RULE_DISABLE_FAILED_1005)

    if not success:
        raise_not_found_exception()


@router.put("/{id}/trigger", status_code=status.HTTP_204_NO_CONTENT)
async def trigger_alert(
    rule_svc: Annotated[RuleService, Depends(get_rule_service)],
    issue_svc: Annotated[IssueService, Depends(get_issue_service)],
    email_svc: Annotated[EmailService, Depends(get_email_service)],
    user: Annotated[User, Depends(get_current_user)],
    id: int,
):
    rule = rule_svc.show(user, id)
    if rule is None:
        raise_not_found_exception()

    try:
        issue = issue_svc.create(rule)
        if issue is None:
            raise Exception

        subject = get_formatted_string_from_template(
            TemplatePath.ISSUE_TITLE.value,
            rule_name=rule.name or rule.id,
        )
        content = get_formatted_string_from_template(
            TemplatePath.ISSUE_CONTENT.value,
        )
        email_svc.send_noreply([user.email], subject, content)
    except Exception:
        raise_custom_exception(ResponseCode.RULE_TRIGGER_FAILED_1006)
