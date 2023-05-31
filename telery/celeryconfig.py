from celery.schedules import crontab

broker_url = "pyamqp://localhost"
result_backend = "rpc://"

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
# TODO: Asia/Taipei doesn't work
timezone = "UTC"

imports = ["telery.crawler_tasks"]

beat_schedule = {
    "Earthquake": {
        "task": "telery.crawler_tasks.Earthquake",
        "schedule": crontab(minute="5"),
        "args": (2020, 5),
    },
    "Reservoir": {
        "task": "telery.crawler_tasks.Reservoir",
        "schedule": crontab(minute="5"),
        "args": (2020, 5, 1),
    },
    "Power": {
        "task": "telery.crawler_tasks.Power",
        "schedule": crontab(minute="5"),
        "args": (),
    },
}
