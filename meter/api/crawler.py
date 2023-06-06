from typing import Annotated

from fastapi import APIRouter, Depends

from meter.api import get_crawler_service
from meter.domain.crawler import CrawlerService

router = APIRouter()


@router.get("/power")
async def get_all_power(
    svc: Annotated[CrawlerService, Depends(get_crawler_service)],
):
    return svc.get_all_power()


@router.get("/eq")
async def get_all_eq(
    svc: Annotated[CrawlerService, Depends(get_crawler_service)],
):
    return svc.get_all_eq()


@router.get("/dam")
async def get_all_dam(
    svc: Annotated[CrawlerService, Depends(get_crawler_service)],
):
    return svc.get_all_dam()
