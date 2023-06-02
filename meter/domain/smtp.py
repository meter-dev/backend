import os
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

from meter.domain import SMTPServerParam


class EmailService:
    def __init__(self, config: SMTPServerParam) -> None:
        self.config = config

    def send(self, from_addr, password, to_addrs, subject, text, html):
        with SMTP(self.config.server, 587) as server:
            if password is not None:
                server.login(from_addr, password)
            msg = MIMEMultipart("alternative")
            msg["From"] = from_addr
            msg["To"] = ", ".join(to_addrs)
            msg["Subject"] = subject
            msg.attach(MIMEText(text, "plain"))
            msg.attach(MIMEText(html, "html"))
            server.send_message(msg, from_addr, to_addrs)

    def send_noreply(self, to_addrs, subject, text, html=None):
        args = (
            self.config.noreply,
            self.config.noreply_password,
            to_addrs,
            subject,
            text,
            html or text,
        )
        threading.Thread(target=self.send, args=args).start()
