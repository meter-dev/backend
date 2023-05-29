from pprint import pprint

from crawler.eq import EqCrawler
from crawler.dam import DamCrawler
from crawler.power import PowerCrawler

import asyncio

if __name__ == '__main__':
    # Earthquake
    eq = EqCrawler([{'year': 2023, 'month': 5}])
    asyncio.run(eq.crawl())
    report = list(eq.report())
    pprint(report)

    # Reservoir
    dam = DamCrawler([{'year': 2023, 'month': 5, 'day': 28}])
    asyncio.run(dam.crawl())
    report = list(dam.report())
    pprint(report)

    # Power
    power = PowerCrawler()
    asyncio.run(power.crawl())
    report = list(power.report())
    pprint(report)
