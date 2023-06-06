from typing import Annotated

from fastapi import APIRouter, Depends

from crawler.model import Dam, Eq, PowerReturn
from meter.api import get_report_service
from meter.domain.report import ReportService

router = APIRouter()


@router.get(
    "/power",
    response_model=list[PowerReturn],
)
async def get_all_power(
    svc: Annotated[ReportService, Depends(get_report_service)],
):
    return svc.get_all_power()


@router.get(
    "/eq",
    response_model=list[Eq],
)
async def get_all_eq(
    svc: Annotated[ReportService, Depends(get_report_service)],
):
    return svc.get_all_eq()


@router.get(
    "/dam",
    response_model=list[Dam],
)
async def get_all_dam(
    svc: Annotated[ReportService, Depends(get_report_service)],
):
    return svc.get_all_dam()
