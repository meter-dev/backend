from sqlmodel import Session, select

from crawler.model import Dam, Eq, Power


class CrawlerService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all_power(self):
        powers = self.session.exec(select(Power)).all()
        new_powers = []
        for power in powers:
            power = power.dict()
            whole = {
                "load": 0,
                "max_supply": 0,
                "recv_rate": None,
            }
            for k in ("east", "central", "south", "north"):
                whole["load"] += power[k]["load"]
                whole["max_supply"] += power[k]["max_supply"]

            whole["recv_rate"] = whole["max_supply"] / whole["load"] / whole["load"]
            power["whole"] = whole
            new_powers.append(power)

        return new_powers

    def get_all_eq(self):
        return self.session.exec(select(Eq)).all()

    def get_all_dam(self):
        return self.session.exec(select(Dam)).all()
