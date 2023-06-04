import time
from datetime import datetime
from typing import TypedDict
from urllib.parse import urlencode

import httpx
from sqlmodel import SQLModel

from .crawler import Crawler


class DamReport(SQLModel):
    name: str
    timestamp: int
    storage: float
    percent: float


class DamQuery(TypedDict):
    year: int
    month: int
    day: int


def getval(data: str, name: str):
    delim = f'id="{name}" value="'
    val = data[data.find(delim) + len(delim) :]
    val = val[: val.find('"')]
    return val


def payload():
    r = httpx.get("https://fhy.wra.gov.tw/ReservoirPage_2011/Statistics.aspx")
    data = r.text
    return urlencode(
        {
            "__EVENTTARGET": "ctl00$cphMain$btnQuery",
            "__EVENTVALIDATION": getval(data, "__EVENTVALIDATION"),
            "__VIEWSTATE": getval(data, "__VIEWSTATE"),
            "__VIEWSTATEGENERATOR": getval(data, "__VIEWSTATEGENERATOR"),
        }
    )


HEADERS = {"content-type": "application/x-www-form-urlencoded"}


def damname(s: str):
    return s[s.find(">") + 1 : s.find("<")]


def timestamp(timestr: str):
    timestr = timestr[1:]
    if timestr == "--":
        return -1
    return int(time.mktime(datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S").timetuple()))


def damstorage(c: str):
    c = c[c.find(">") + 1 :]
    if c == "--":
        return -1
    return float(c.replace(",", ""))


def dampercent(p: str):
    p = p[p.find(">") + 1 :]
    if p == "--":
        return -1
    return float(p[:-2])


class DamCrawler(Crawler[DamReport, DamQuery], method="post", headers=HEADERS):
    URL = "https://fhy.wra.gov.tw/ReservoirPage_2011/Statistics.aspx"

    def _url(self, query: DamQuery):
        return self.URL

    def _data(self, query: DamQuery):
        return payload() + urlencode(
            {
                "ctl00$cphMain$ucDate$cboYear": query["year"],
                "ctl00$cphMain$ucDate$cboMonth": query["month"],
                "ctl00$cphMain$ucDate$cboDay": query["day"],
            }
        )

    def _report(self, data: bytes):
        dams = data.decode().split('<a href="ReservoirChart.aspx?key=')[1:]
        for dam in dams:
            dam = dam.split("</td><td")
            yield DamReport(
                name=damname(dam[0]),
                timestamp=timestamp(dam[1]),
                storage=damstorage(dam[6]),
                percent=dampercent(dam[7]),
            )
