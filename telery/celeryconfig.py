from celery.schedules import crontab

broker_url = "pyamqp://localhost"
result_backend = "rpc://"

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Asia/Taipei"
enable_utc = True

imports = ["telery.crawler_tasks"]

# TODO: check why celery beat can't run with crontab
beat_schedule = {
    "Earthquake": {
        "task": "telery.crawler_tasks.Earthquake",
        "schedule": 300,
        "args": (2020, 5),
    },
    "Reservoir": {
        "task": "telery.crawler_tasks.Reservoir",
        "schedule": 300,
        "args": (2020, 5, 1),
    },
    "Power": {
        "task": "telery.crawler_tasks.Power",
        "schedule": 300,
        "args": (),
    },
}
