from typing import Annotated

from fastapi import APIRouter, Depends, status

from meter.api import get_current_user, get_issue_service
from meter.constant.issue_status import IssueStatus
from meter.constant.response_code import ResponseCode
from meter.domain.issue import IssueService, ReadIssue, ReadIssueDetail, UpdateIssue
from meter.domain.user import User
from meter.helper import raise_custom_exception, raise_not_found_exception

router = APIRouter()


@router.get(
    "/",
    response_model=list[ReadIssue],
)
async def get_issues(
    svc: Annotated[IssueService, Depends(get_issue_service)],
    user: Annotated[User, Depends(get_current_user)],
    status: IssueStatus | None = None,
):
    filter = {
        "status": status,
    }
    return svc.get(user, filter)


@router.get(
    "/{id}",
    response_model=ReadIssueDetail,
)
async def get_issue(
    svc: Annotated[IssueService, Depends(get_issue_service)],
    user: Annotated[User, Depends(get_current_user)],
    id: int,
):
    issue = svc.show(user, id)
    if issue is None:
        raise_not_found_exception()

    return issue


@router.patch(
    "/{id}",
    response_model=ReadIssueDetail,
)
async def update_issue(
    svc: Annotated[IssueService, Depends(get_issue_service)],
    user: Annotated[User, Depends(get_current_user)],
    id: int,
    input: UpdateIssue,
):
    issue = None

    try:
        issue = svc.update(id, input, user)
    except Exception:
        raise_custom_exception(ResponseCode.ISSUE_UPDATE_FAILED_1101)

    if issue is None:
        raise_not_found_exception()

    return issue


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(
    svc: Annotated[IssueService, Depends(get_issue_service)],
    user: Annotated[User, Depends(get_current_user)],
    id: int,
):
    success = False

    try:
        success = svc.delete(id, user)
    except Exception:
        raise_custom_exception(ResponseCode.ISSUE_DELETE_FAILED_1102)

    if not success:
        raise_not_found_exception()
