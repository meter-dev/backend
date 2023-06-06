from sqlmodel import Session, select

from crawler.model import Dam, Eq, Power


class CrawlerService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_power(self, id: str) -> Power:
        power = self.session.get(Power, id)
        return power

    def get_eq(self, id: str) -> Eq:
        eq = self.session.get(Eq, id)
        return eq

    def get_dam(self, id: str) -> Dam:
        dam = self.session.get(Dam, id)
        return dam

    def get_all_power(self):
        return self.session.exec(select(Power.id, Power.timestamp)).all()

    def get_all_eq(self):
        return self.session.exec(select(Eq.id, Eq.timestamp)).all()

    def get_all_dam(self):
        return self.session.exec(select(Dam.id, Dam.timestamp)).all()
