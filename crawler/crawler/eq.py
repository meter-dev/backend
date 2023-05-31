import json
import math
import time
from datetime import datetime
from typing import Literal, TypedDict

from .crawler import Crawler

Point = tuple[float, float]
Intensity = tuple[int, int, int]


class Geometry(TypedDict):
    type: Literal["Point"]
    coordinates: Point


class EqReport(TypedDict):
    timestamp: int
    geometry: Geometry
    scale: float
    intensity: Intensity
    link: str
    img: str


class EqQuery(TypedDict):
    year: int
    month: int


def geojson(point: Point):
    return Geometry(type="Point", coordinates=point)


def timestamp(timestr: str):
    return int(time.mktime(datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S").timetuple()))


def rad2deg(rad: float):
    deg = rad * 180 / math.pi
    return deg


def deg2rad(deg: float):
    rad = deg * math.pi / 180
    return rad


def geodist(p1: Point, p2: Point):
    theta = p1[0] - p2[0]
    dist = (
        60
        * 1.1515
        * rad2deg(
            math.acos(
                (math.sin(deg2rad(p1[1])) * math.sin(deg2rad(p2[1])))
                + (
                    math.cos(deg2rad(p1[1]))
                    * math.cos(deg2rad(p2[1]))
                    * math.cos(deg2rad(theta))
                )
            )
        )
    )
    return dist * 1.609344


def intensity(scale: float, depth: float, center: Point) -> Intensity:
    params = [
        (121.010, 24.7730, 1.758),
        (120.618, 24.2115, 1.063),
        (120.272, 23.1135, 1.968),
    ]
    intens: list[int] = []
    for p in params:
        dist = geodist(center, (p[0], p[1]))
        r = math.sqrt(dist**2 + depth**2)
        pga = 1.657 * (math.e ** (1.533 * scale)) * (r**-1.607) * p[2]
        if pga < 80:
            if pga < 0.8:
                inten = 0
            elif pga < 2.5:
                inten = 1
            elif pga < 8.0:
                inten = 2
            elif pga < 25:
                inten = 3
            else:
                inten = 4
        else:
            pgv = pga / 8.6561
            if pgv < 15:
                inten = 4
            if pgv < 50:
                inten = 5
            if pgv < 140:
                inten = 6
            else:
                inten = 7
        intens.append(inten)
    return tuple(intens)


HEADERS = {"content-type": "application/x-www-form-urlencoded"}


class EqCrawler(Crawler[EqReport, EqQuery], method="post", headers=HEADERS):
    URL = "https://scweb.cwb.gov.tw/zh-tw/earthquake/ajaxhandler"
    PAYLOAD = "draw=3&columns%5B0%5D%5Bdata%5D=0&columns%5B0%5D%5Bname%5D=EventNo&columns%5B0%5D%5Bsearchable%5D=false&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=1&columns%5B1%5D%5Bname%5D=MaxIntensity&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=2&columns%5B2%5D%5Bname%5D=OriginTime&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=3&columns%5B3%5D%5Bname%5D=MagnitudeValue&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=4&columns%5B4%5D%5Bname%5D=Depth&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=5&columns%5B5%5D%5Bname%5D=Description&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=6&columns%5B6%5D%5Bname%5D=Description&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=2&order%5B0%5D%5Bdir%5D=desc&start=0&length=50&search%5Bvalue%5D=&search%5Bregex%5D=false&Search={year}%E5%B9%B4{month}%E6%9C%88&txtSDate=&txtEDate=&txtSscale=&txtEscale=&txtSdepth=&txtEdepth=&txtLonS=&txtLonE=&txtLatS=&txtLatE=&ddlCity=&ddlTown=&ddlCitySta=&ddlStation=&txtIntensityB=&txtIntensityE=&txtLon=&txtLat=&txtKM=&ddlStationName=------&cblEventNo=&txtSDatePWS=&txtEDatePWS=&txtSscalePWS=&txtEscalePWS=&ddlMark="

    def _url(self, query: EqQuery):
        return self.URL

    def _data(self, query: EqQuery):
        return self.PAYLOAD.format(**query).encode()

    def _report(self, data: bytes):
        eq: list[list[str]] = json.loads(data.decode())["data"]
        for d in eq:
            scale = float(d[3])
            depth = float(d[4])
            loc = (float(d[7]), float(d[8]))
            yield EqReport(
                timestamp=timestamp(d[2]),
                geometry=geojson(loc),
                scale=scale,
                intensity=intensity(scale, depth, loc),
                link=f"https://scweb.cwb.gov.tw/zh-tw/earthquake/imgs/{d[0]}",
                img=f"https://scweb.cwb.gov.tw/webdata/OLDEQ/{d[0][:6]}/{d[0]}_H.png",
            )
