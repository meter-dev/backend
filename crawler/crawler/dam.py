from datetime import datetime
from urllib.parse import urlencode

from .crawler import Crawler

import time

import httpx


def getval(data, name):
    delim = f'id="{name}" value="'
    val = data[data.find(delim) + len(delim):]
    val = val[:val.find('"')]
    return val


def payload():
    r = httpx.get('https://fhy.wra.gov.tw/ReservoirPage_2011/Statistics.aspx')
    data = r.text
    return urlencode({
        '__EVENTTARGET':
        'ctl00$cphMain$btnQuery',
        '__EVENTVALIDATION':
        getval(data, '__EVENTVALIDATION'),
        '__VIEWSTATE':
        getval(data, '__VIEWSTATE'),
        '__VIEWSTATEGENERATOR':
        getval(data, '__VIEWSTATEGENERATOR')
    })


HEADERS = {'content-type': 'application/x-www-form-urlencoded'}


def damname(s):
    return s[s.find('>') + 1:s.find('<')]


def timestamp(t):
    t = t[1:]
    if t == '--':
        return -1
    return int(
        time.mktime(datetime.strptime(t, "%Y-%m-%d %H:%M:%S").timetuple()))


def damstorage(c):
    c = c[c.find('>') + 1:]
    if c == '--':
        return -1
    return float(c.replace(',', ''))


def dampercent(p):
    p = p[p.find('>') + 1:]
    if p == '--':
        return -1
    return float(p[:-2])


class DamCrawler(Crawler, method='post', headers=HEADERS):
    URL = 'https://fhy.wra.gov.tw/ReservoirPage_2011/Statistics.aspx'

    def _url(self, _):
        return self.URL

    def _data(self, query):
        return payload() + urlencode(
            {
                'ctl00$cphMain$ucDate$cboYear': query['year'],
                'ctl00$cphMain$ucDate$cboMonth': query['month'],
                'ctl00$cphMain$ucDate$cboDay': query['day']
            })

    def _report(self, data):
        data = data.split('<a href="ReservoirChart.aspx?key=')[1:]
        for dam in data:
            dam = dam.split('</td><td')
            yield {
                'name': damname(dam[0]),
                'timestamp': timestamp(dam[1]),
                'storage': damstorage(dam[6]),
                'percent': dampercent(dam[7])
            }
