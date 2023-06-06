import asyncio

from sqlmodel import Session, SQLModel, create_engine, select

from .crawler.dam import DamCrawler
from .crawler.eq import EqCrawler
from .crawler.power import PowerCrawler
from .model import Dam, Eq, Power, save_crawler_report

if __name__ == "__main__":
    # TODO: get the engine from elsewhere
    sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    engine = create_engine(sqlite_url, echo=True)
    SQLModel.metadata.create_all(engine)

    # Earthquake
    eq = EqCrawler([{"year": 2023, "month": 5}])
    asyncio.run(eq.crawl())
    report = list(eq.report())
    save_crawler_report(engine, Eq, report)

    # Reservoir
    dam = DamCrawler([{"year": 2023, "month": 5, "day": 28}])
    asyncio.run(dam.crawl())
    report = list(dam.report())
    save_crawler_report(engine, Dam, report)

    # Power
    power = PowerCrawler()
    asyncio.run(power.crawl())
    report = list(power.report())
    save_crawler_report(engine, Power, report)

    with Session(engine) as session:
        stmt = select(Eq).where(Eq.scale >= 4)
        results = session.exec(stmt)
        for r in results:
            print(r.geometry["coordinates"])
