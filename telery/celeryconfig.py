from celery.schedules import crontab

broker_url = "pyamqp://localhost"
result_backend = "rpc://"

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Asia/Taipei"

imports = ["telery.crawler_tasks", "telery.save_tasks"]

beat_schedule = {
    "SaveEarthquake": {
        "task": "telery.save_tasks.SaveNowEarthquake",
        "schedule": crontab(minute="*/1"),
        "args": (),
    },
    "SaveReservoir": {
        "task": "telery.save_tasks.SaveNowReservoir",
        "schedule": crontab(minute="*/1"),
        "args": (),
    },
    "SavePower": {
        "task": "telery.save_tasks.SaveNowPower",
        "schedule": crontab(minute="*/1"),
        "args": (),
    },
}
