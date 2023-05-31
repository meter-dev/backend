import asyncio

from crawler.crawler.dam import DamCrawler
from crawler.crawler.eq import EqCrawler
from crawler.crawler.power import PowerCrawler
from telery import app


@app.task
def Earthquake(year: int, month: int):
    eq = EqCrawler([{"year": year, "month": month}])
    asyncio.run(eq.crawl())
    report = list(eq.report())
    return report


@app.task
def Reservoir(year: int, month: int, day: int):
    dam = DamCrawler([{"year": year, "month": month, "day": day}])
    asyncio.run(dam.crawl())
    report = list(dam.report())
    return report


@app.task
def Power():
    power = PowerCrawler()
    asyncio.run(power.crawl())
    report = list(power.report())
    return report


@app.task
def nowEarthquake():
    now_time = time.localtime()
    now_time.tm_mon = 5  # for test
    eq = EqCrawler([{"year": now_time.tm_year, "month": now_time.tm_mon}])
    asyncio.run(eq.crawl())
    report = list(eq.report())
    return report


@app.task
def nowReservoir():
    now_time = time.localtime()
    now_time.tm_mon = 5  # for test
    dam = DamCrawler(
        [{"year": now_time.tm_year, "month": now_time.tm_mon, "day": now_time.tm_mday}]
    )
    asyncio.run(dam.crawl())
    report = list(dam.report())
    return report