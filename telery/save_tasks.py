import json
import time
from pprint import pprint

from celery import chain

from telery import app
from telery.crawler_tasks import NowEarthquake, NowReservoir, Power


@app.task
def SavePower(data):
    pprint(data)
    with open(
        "Power " + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".json", "w"
    ) as f:
        json.dump(data, f)


@app.task
def SaveEarthquake(data):
    with open(
        "Earthquake " + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".json",
        "w",
    ) as f:
        json.dump(data, f)


@app.task
def SaveReservoir(data):
    with open(
        "Reservoir " + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".json",
        "w",
    ) as f:
        json.dump(data, f)


@app.task
def SaveNowEarthquake():
    tasks = NowEarthquake.s() | SaveEarthquake.s()
    chain(tasks).apply_async()


@app.task
def SaveNowReservoir():
    tasks = NowReservoir.s() | SaveReservoir.s()
    chain(tasks).apply_async()


@app.task
def SaveNowPower():
    tasks = Power.s() | SavePower.s()
    chain(tasks).apply_async()
