from tasks import Earthquake, Reservoir, Power, add
import time
from pprint import pprint

if __name__ == '__main__':
    result = Earthquake.delay(2023, 5)
    while not result.ready():
        time.sleep(1)
    pprint(result.get())

# TODO: docker-compose
# celery -A tasks worker --loglevel=DEBUG
# docker run --rm -p 5672:5672 -p 15672:15672 rabbitmq:3.12-rc-management-alpine