from sqlmodel import Session, create_engine

from meter.api import MeterConfig
from meter.domain.issue import IssueService
from meter.domain.smtp import EmailService
from meter.job.trigger_rule import TriggerRuleJob
from telery import app

from .dbconfig import db_url


@app.task
def watch_new_data():
    engine = create_engine(db_url)
    session = Session(engine)
    smtp = MeterConfig().smtp
    email_svc = EmailService(smtp)
    issue_svc = IssueService(session)

    job = TriggerRuleJob(session, email_svc, issue_svc)
    job.trigger_over_threshold()
    return "ok"
