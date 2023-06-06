import time
from pprint import pprint

from telery.crawler_tasks import (
    crawl_earthquake,
    crawl_now_earthquake,
    crawl_now_reservoir,
    crawl_power,
    crawl_reservoir,
)

if __name__ == "__main__":
    result = crawl_power.delay()
    while not result.ready():
        time.sleep(1)
    pprint(result.get())

# TODO: docker-compose
# celery -A tasks worker --loglevel=DEBUG -B
# celery -A telery worker --loglevel=INFO
# celery -A telery beat --loglevel=INFO
# docker run --rm -p 5672:5672 -p 15672:15672 rabbitmq:3.12-rc-management-alpine
