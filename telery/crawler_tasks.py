import asyncio
import time

from sqlmodel import create_engine

from crawler.crawler.dam import DamCrawler
from crawler.crawler.eq import EqCrawler
from crawler.crawler.power import PowerCrawler
from crawler.model import Dam, Eq, Power, save_crawler_report
from telery import app

from .dbconfig import db_url


@app.task
def crawl_earthquake(year: int, month: int):
    eq = EqCrawler([{"year": year, "month": month}])
    asyncio.run(eq.crawl())
    report = list(eq.report())
    engine = create_engine(db_url)
    save_crawler_report(engine, Eq, report)
    return len(report)


@app.task
def crawl_reservoir(year: int, month: int, day: int):
    dam = DamCrawler([{"year": year, "month": month, "day": day}])
    asyncio.run(dam.crawl())
    report = list(dam.report())
    engine = create_engine(db_url)
    save_crawler_report(engine, Dam, report)
    return len(report)


@app.task
def crawl_power():
    power = PowerCrawler()
    asyncio.run(power.crawl())
    report = list(power.report())
    engine = create_engine(db_url)
    save_crawler_report(engine, Power, report)
    return len(report)


@app.task
def crawl_now_earthquake():
    now_time = time.localtime()
    eq = EqCrawler([{"year": now_time.tm_year, "month": now_time.tm_mon}])
    asyncio.run(eq.crawl())
    report = list(eq.report())
    engine = create_engine(db_url)
    save_crawler_report(engine, Eq, report)
    return len(report)


@app.task
def crawl_now_reservoir():
    now_time = time.localtime()
    dam = DamCrawler(
        [{"year": now_time.tm_year, "month": now_time.tm_mon, "day": now_time.tm_mday}]
    )
    asyncio.run(dam.crawl())
    report = list(dam.report())
    engine = create_engine(db_url)
    save_crawler_report(engine, Eq, report)
    return len(report)
