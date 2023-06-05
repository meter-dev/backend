from typing import Literal, Optional, TypedDict

from sqlalchemy import JSON
from sqlmodel import Column, Field, Session, SQLModel, UniqueConstraint

# TODO: Maybe we could store `Eq.geometry`, `Eq.intensity`, and the columns
#       under `Power` in alternative data types instead of `JSON`.


class DamReport(SQLModel):
    name: str = Field(index=True)
    timestamp: int = Field(index=True)
    storage: float
    percent: float


class Dam(DamReport, table=True):
    __table_args__ = (UniqueConstraint("name", "timestamp"),)
    id: Optional[int] = Field(default=None, primary_key=True)


Point = tuple[float, float]
Intensity = tuple[int, int, int]


class Geometry(TypedDict):
    type: Literal["Point"]
    coordinates: Point


class EqReport(SQLModel):
    timestamp: int = Field(index=True)
    geometry: Geometry = Field(sa_column=Column(JSON), nullable=False)
    scale: float
    intensity: Intensity = Field(sa_column=Column(JSON), nullable=False)
    link: str
    img: str


class Eq(EqReport, table=True):
    __table_args__ = (UniqueConstraint("timestamp"),)
    id: Optional[int] = Field(default=None, primary_key=True)


class PowerAreaReport(TypedDict):
    load: float
    max_supply: float
    recv_rate: float


class PowerReport(SQLModel):
    timestamp: int = Field(index=True)
    east: PowerAreaReport = Field(sa_column=Column(JSON), nullable=False)
    south: PowerAreaReport = Field(sa_column=Column(JSON), nullable=False)
    central: PowerAreaReport = Field(sa_column=Column(JSON), nullable=False)
    north: PowerAreaReport = Field(sa_column=Column(JSON), nullable=False)


class Power(PowerReport, table=True):
    __table_args__ = (UniqueConstraint("timestamp"),)
    id: Optional[int] = Field(default=None, primary_key=True)


def save_crawler_report(engine, model, report):
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
