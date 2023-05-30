from datetime import datetime
from typing import Any, TypedDict

from .crawler import Crawler

import time

import httpx


class PowerAreaReport(TypedDict):
    load: float
    max_supply: float
    recv_rate: float


class PowerReport(TypedDict):
    timestamp: int
    east: PowerAreaReport
    south: PowerAreaReport
    central: PowerAreaReport
    north: PowerAreaReport


def mxpowersply():
    r = httpx.get(
        'https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/loadpara.json'
    )
    data = r.json()
    mxsply = float(data['records'][1]['fore_maxi_sply_capacity'])

    # https://github.com/TaiwanStat/real.taiwanstat.com/blob/a88daf06f6e34df99ed048c1f5376e3188dd0d4a/power/js/index.js#L16
    SPLY_RATE = [0.022, 0.32, 0.33, 0.35]

    return list(map(lambda r: r * mxsply, SPLY_RATE))


def timestamp(timestr: str):
    t = timestr.split(':')
    if len(t) < 2:
        t.append('0')
    now = datetime.now()
    t = datetime(now.year, now.month, now.day, int(t[0]), int(t[1]))
    return int(time.mktime(t.timetuple()))


IDontCare = Any


class PowerCrawler(Crawler[PowerReport, IDontCare], method='get'):
    URL = 'https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/loadareas.csv'

    def _url(self, query: Any):
        return self.URL

    def _data(self, query: Any):
        return ''

    def _report(self, data: bytes):
        lines = data.decode().split('\r\n')
        lines = list(filter(lambda d: len(d) > 2, lines))
        for line in lines:
            d = line.split(',')
            load = list(map(float, d[1:]))
            recv = list(map(lambda s, l: (s - l) / l * 100, self.supply, load))
            yield PowerReport(
                timestamp=timestamp(d[0]),
                east=PowerAreaReport(load=load[0],
                                     max_supply=round(self.supply[0], 2),
                                     recv_rate=round(recv[0], 2)),
                south=PowerAreaReport(load=load[1],
                                      max_supply=round(self.supply[1], 2),
                                      recv_rate=round(recv[1], 2)),
                central=PowerAreaReport(load=load[2],
                                        max_supply=round(self.supply[2], 2),
                                        recv_rate=round(recv[2], 2)),
                north=PowerAreaReport(load=load[3],
                                      max_supply=round(self.supply[3], 2),
                                      recv_rate=round(recv[3], 2)))

    async def crawl(self):
        self.supply = mxpowersply()
        return await super().crawl()
