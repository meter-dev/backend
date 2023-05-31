import abc

import httpx


class Crawler(metaclass=abc.ABCMeta):

    def __init_subclass__(cls, method, headers={}):
        cls.METHOD = method
        cls.HEADERS = headers

    def __init__(self, queries=None):
        if queries is None:
            queries = [...]
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
        client = httpx.AsyncClient()
        for url, data in zip(self.urls, self.data):
            r = await client.request(self.METHOD,
                                     url,
                                     content=data,
                                     headers=self.HEADERS)
            self.done.append(r.text)
        await client.aclose()
