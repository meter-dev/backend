import abc

import aiohttp
import certifi
import ssl

SSLCTX = ssl.create_default_context(cafile=certifi.where())


class Crawler(metaclass=abc.ABCMeta):

    def __init_subclass__(cls, method, headers={}):
        cls.METHOD = method
        cls.HEADERS = headers

    def __init__(self, queries):
        self.queries = queries
        self.done = []

    @abc.abstractmethod
    def _url(self, query):
        return NotImplemented

    @abc.abstractmethod
    def _data(self, query):
        return NotImplemented

    @abc.abstractmethod
    def _report(self, data):
        return NotImplemented

    @property
    def urls(self):
        for query in self.queries:
            yield self._url(query)

    @property
    def data(self):
        for query in self.queries:
            yield self._data(query)

    def report(self):
        for data in self.done:
            yield from self._report(data)

    async def crawl(self):
        async with aiohttp.ClientSession() as session:
            for url, data in zip(self.urls, self.data):
                async with session.request(self.METHOD,
                                           url,
                                           data=data,
                                           headers=self.HEADERS,
                                           ssl=SSLCTX) as resp:
                    self.done.append(await resp.text())
