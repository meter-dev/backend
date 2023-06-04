import abc
import asyncio
from typing import Generic, Iterable, Iterator, Optional, TypeVar

import httpx
from httpx import Response
from httpx._types import HeaderTypes, RequestContent, URLTypes

Report = TypeVar("Report")
Query = TypeVar("Query")


class Crawler(Generic[Report, Query], metaclass=abc.ABCMeta):
    METHOD: str
    HEADERS: Optional[HeaderTypes]

    def __init_subclass__(cls, method: str, headers: Optional[HeaderTypes] = None):
        cls.METHOD = method
        cls.HEADERS = headers

    def __init__(self, queries: Iterable[Query] = [...]):
        self.queries = queries
        self.done: list[bytes] = []

    @abc.abstractmethod
    def _url(self, query: Query) -> URLTypes:
        return NotImplemented

    @abc.abstractmethod
    def _data(self, query: Query) -> RequestContent:
        return NotImplemented

    @abc.abstractmethod
    def _report(self, data: bytes) -> Iterator[Report]:
        yield NotImplemented

    @property
    def urls(self) -> Iterator[URLTypes]:
        for query in self.queries:
            yield self._url(query)

    @property
    def data(self) -> Iterator[RequestContent]:
        for query in self.queries:
            yield self._data(query)

    def report(self) -> Iterator[Report]:
        for data in self.done:
            yield from self._report(data)

    async def crawl(self):
        async with httpx.AsyncClient() as client:
            reqs = (
                client.request(self.METHOD, url, content=data, headers=self.HEADERS)
                for url, data in zip(self.urls, self.data)
            )
            resps: list[Response] = await asyncio.gather(*reqs)
            self.done.extend(map(lambda r: r.content, resps))
