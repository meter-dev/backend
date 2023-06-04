import asyncio
from pprint import pprint

from model import Dam, Eq, Power, engine, save_crawl_report
from sqlmodel import Session, SQLModel, select

from crawler.dam import DamCrawler
from crawler.eq import EqCrawler
from crawler.power import PowerCrawler

if __name__ == "__main__":
    SQLModel.metadata.create_all(engine)

    # Earthquake
    eq = EqCrawler([{"year": 2023, "month": 5}])
    asyncio.run(eq.crawl())
    report = list(eq.report())
    save_crawl_report(Eq, report)

    # Reservoir
    dam = DamCrawler([{"year": 2023, "month": 5, "day": 28}])
    asyncio.run(dam.crawl())
    report = list(dam.report())
    save_crawl_report(Dam, report)

    # Power
    power = PowerCrawler()
    asyncio.run(power.crawl())
    report = list(power.report())
    save_crawl_report(Power, report)

    with Session(engine) as session:
        stmt = select(Eq).where(Eq.scale >= 4)
        results = session.exec(stmt)
        for r in results:
            print(r.geometry["coordinates"])
