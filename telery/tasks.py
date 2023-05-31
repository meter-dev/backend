from celery import Celery
import asyncio

from crawler.crawler.eq import EqCrawler
from crawler.crawler.dam import DamCrawler
from crawler.crawler.power import PowerCrawler



app = Celery('celery')
app.config_from_object('celeryconfig')

@app.task
def add(x, y):
    return x + y

@app.task
def Earthquake(year: int, month: int):
    eq = EqCrawler([{'year': year, 'month': month}])
    asyncio.run(eq.crawl())
    report = list(eq.report())
    return report

@app.task
def Reservoir(year: int, month: int, day: int):
    dam = DamCrawler([{'year': year, 'month': month, 'day': day}])
    asyncio.run(dam.crawl())
    report = list(dam.report())
    return report

@app.task
def Power():
    power = PowerCrawler()
    asyncio.run(power.crawl())
    report = list(power.report())
    return report

if __name__ == '__main__':
    app.start()