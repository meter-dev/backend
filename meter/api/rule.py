from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from meter.api import get_current_user, get_rule_service
from meter.domain.rule import CreateRule, ReadRule, RuleService, UpdateRule
from meter.domain.user import User

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
    rule = svc.create(input, user)
    if rule is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return rule


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

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
    rule = svc.update(id, input, user)
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return rule


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    svc: Annotated[RuleService, Depends(get_rule_service)],
    user: Annotated[User, Depends(get_current_user)],
    id: int,
):
    success = svc.delete(id, user)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.put("/{id}/enable", status_code=status.HTTP_204_NO_CONTENT)
async def enable_rule(
    svc: Annotated[RuleService, Depends(get_rule_service)],
    user: Annotated[User, Depends(get_current_user)],
    id: int,
):
    success = svc.enable(id, user)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.put("/{id}/disable", status_code=status.HTTP_204_NO_CONTENT)
async def disable_rule(
    svc: Annotated[RuleService, Depends(get_rule_service)],
    user: Annotated[User, Depends(get_current_user)],
    id: int,
):
    success = svc.disable(id, user)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.put("/{id}/trigger", status_code=status.HTTP_204_NO_CONTENT)
async def trigger_alert(
    svc: Annotated[RuleService, Depends(get_rule_service)],
    user: Annotated[User, Depends(get_current_user)],
    id: int,
):
    pass
