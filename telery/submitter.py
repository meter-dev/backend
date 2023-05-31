import time
from pprint import pprint

from telery.crawler_tasks import (
    Earthquake,
    Power,
    Reservoir,
    nowEarthquake,
    nowReservoir,
)

if __name__ == "__main__":
    now_time = time.localtime()
    print(
        now_time.tm_year,
        now_time.tm_mon,
        now_time.tm_mday,
        type(now_time.tm_year),
        type(now_time.tm_mon),
        type(now_time.tm_mday),
    )
    result = Earthquake.delay(now_time.tm_year, now_time.tm_mon - 1)
    while not result.ready():
        time.sleep(1)
    pprint(result.get())

# TODO: docker-compose
# celery -A tasks worker --loglevel=DEBUG
# celery -A tasks worker --loglevel=DEBUG -B
# docker run --rm -p 5672:5672 -p 15672:15672 rabbitmq:3.12-rc-management-alpine
