from sqlmodel import Session, select

from crawler.model import Dam, Eq, Power, PowerReturn


class ReportService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all_power(self) -> list[PowerReturn]:
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

            whole["recv_rate"] = (whole["max_supply"] - whole["load"]) / whole["load"]
            power["whole"] = whole
            new_powers.append(PowerReturn(**power))

        return new_powers

    def get_all_eq(self) -> list[Eq]:
        return self.session.exec(select(Eq)).all()

    def get_all_dam(self) -> list[Dam]:
        dams = self.session.exec(select(Dam)).all()
        keys = [["石門", "寶山第二", "永和山"], ["鯉魚潭", "德基"], ["南化", "曾文", "烏山頭"]]
        names = ["竹", "中", "南"]
        for key, name in zip(keys, names):
            storage = 0
            all_storage = 0
            for mia in key:
                dam = self.session.exec(
                    select(Dam).where(Dam.name == f"{mia}水庫").order_by(-Dam.timestamp)
                ).first()
                if dam is not None:
                    storage += dam.storage
                    all_storage += dam.storage / dam.percent
            dams.append(
                Dam(
                    name=name,
                    timestamp=0,
                    storage=storage,
                    percent=storage / all_storage,
                )
            )
        return dams
