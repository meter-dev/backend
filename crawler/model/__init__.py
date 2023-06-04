from typing import Optional

from sqlalchemy import JSON
from sqlmodel import Column, Field, Session, UniqueConstraint, create_engine

from crawler.dam import DamReport
from crawler.eq import EqReport
from crawler.power import PowerReport

# TODO: get the engine from elsewhere
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)
# from meter.api import get_config, get_engine
# engine = get_engine(get_config())


# TODO: Maybe we could store `Eq.geometry`, `Eq.intensity`, and the columns
#       under `Power` in alternative data types instead of `JSON`.


class Dam(DamReport, table=True):
    __table_args__ = (UniqueConstraint("name", "timestamp"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    timestamp: int = Field(index=True)


class Eq(EqReport, table=True):
    __table_args__ = (UniqueConstraint("timestamp"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: int = Field(index=True)
    geometry: dict = Field(sa_column=Column(JSON), nullable=False)
    intensity: tuple = Field(sa_column=Column(JSON), nullable=False)


class Power(PowerReport, table=True):
    __table_args__ = (UniqueConstraint("timestamp"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: int = Field(index=True)
    east: dict = Field(sa_column=Column(JSON), nullable=False)
    south: dict = Field(sa_column=Column(JSON), nullable=False)
    central: dict = Field(sa_column=Column(JSON), nullable=False)
    north: dict = Field(sa_column=Column(JSON), nullable=False)


def save_crawl_report(model, report):
    with Session(engine) as session:
        for r in report:
            session.add(model(**r.dict()))
            # TODO: Upsert the report.
            #       It appears that sqlmodel does not support either the
            #       `UPSERT` or `INSERT OR IGNORE` operations.
            try:
                session.commit()
            except:
                session.rollback()
