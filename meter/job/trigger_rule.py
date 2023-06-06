from datetime import datetime
from typing import List

from sqlmodel import Session, desc, select

from crawler.model import Dam, Eq, Power
from meter.constant.dam_chinese_name import DamChineseName
from meter.constant.rule_operator import RuleOperator
from meter.constant.rule_position import RulePosition
from meter.constant.rule_resource import RuleResource
from meter.domain.issue import IssueService
from meter.domain.rule import Rule
from meter.domain.smtp import EmailService


class TriggerRuleJob:
    def __init__(
        self,
        session: Session,
        email_svc: EmailService,
        issue_svc: IssueService,
    ) -> None:
        self.session = session
        self.email_svc = email_svc
        self.issue_svc = issue_svc

    def is_reservoir(self, location: RulePosition):
        return location in [
            RulePosition.SHIMEN_RESERVOIR,
            RulePosition.FEITSUI_RESERVOIR,
            RulePosition.SECOND_BAOSHAN_RESERVOIR,
            RulePosition.YONGHESHAN_RESERVOIR,
            RulePosition.MINGDE_RESERVOIR,
            RulePosition.LIYUTAN_RESERVOIR,
            RulePosition.DEJI_RESERVOIR,
            RulePosition.SHIGANG_DAM,
            RulePosition.WUSHE_RESERVOIR,
            RulePosition.SUN_MOON_LAKE_RESERVOIR,
            RulePosition.JIJI_WEIR,
            RulePosition.HUSHAN_RESERVOIR,
            RulePosition.RENYITAN_RESERVOIR,
            RulePosition.BAIHE_RESERVOIR,
            RulePosition.WUSHANTOU_RESERVOIR,
            RulePosition.ZENGWEN_RESERVOIR,
            RulePosition.NANHUA_RESERVOIR,
            RulePosition.AGONGDIAN_RESERVOIR,
            RulePosition.GAOPING_RIVER_WEIR,
            RulePosition.MUDAN_RESERVOIR,
        ]

    def is_electricity(self, location: RulePosition):
        return location in [
            RulePosition.EAST_ELECTRICITY,
            RulePosition.SOUTH_ELECTRICITY,
            RulePosition.CENTRAL_ELECTRICITY,
            RulePosition.NORTH_ELECTRICITY,
        ]

    def is_earthquake(self, location: RulePosition):
        return location in [
            RulePosition.HSINCHU_EARTHQUAKE,
            RulePosition.TAICHUNG_EARTHQUAKE,
            RulePosition.TAINAN_EARTHQUAKE,
        ]

    def __get_all_enable_rules(self) -> List[Rule]:
        statement = select(Rule).where(Rule.is_enable == True)
        results = self.session.exec(statement)
        return results.all()

    def __first_reservoir_by_operator(
        self,
        position: RulePosition,
        resource: RuleResource,
        operator: RuleOperator,
        value: float,
        last_triggered_by: datetime | None,
    ) -> Dam | None:
        resource_str = resource.lower()
        name = DamChineseName[position]

        statement = (
            select(Dam).where(Dam.name == name).order_by(desc(Dam.timestamp)).limit(1)
        )

        # avoid triggered by same data
        if last_triggered_by is not None:
            timestamp = int(last_triggered_by.timestamp())
            statement = statement.where(Dam.timestamp != timestamp)

        if operator == RuleOperator.EQUAL_TO:
            statement = statement.where(getattr(Dam, resource_str) == value)
        elif operator == RuleOperator.GREATER_THAN:
            statement = statement.where(getattr(Dam, resource_str) > value)
        elif operator == RuleOperator.GREATER_THAN_OR_EQUAL_TO:
            statement = statement.where(getattr(Dam, resource_str) >= value)
        elif operator == RuleOperator.LESS_THAN:
            statement = statement.where(getattr(Dam, resource_str) < value)
        elif operator == RuleOperator.LESS_THAN_OR_EQUAL_TO:
            statement = statement.where(getattr(Dam, resource_str) <= value)

        results = self.session.exec(statement)
        return results.first()

    def __get_latest_eletricity(
        self,
    ) -> Power | None:
        statement = select(Power).order_by(desc(Power.timestamp)).limit(1)
        results = self.session.exec(statement)
        return results.first()

    def __get_all_earthquakes(self) -> List[Eq]:
        statement = select(Eq.intensity, Eq.timestamp, Eq.id).order_by(
            desc(Eq.timestamp)
        )
        results = self.session.exec(statement)
        return results.fetchall()

    def __first_earthquake_by_operator(self, rule: Rule) -> Eq | None:
        if rule.position == RulePosition.HSINCHU_EARTHQUAKE:
            index = 0
        elif rule.position == RulePosition.TAICHUNG_EARTHQUAKE:
            index = 1
        else:  # RulePosition.TAINAN_EARTHQUAKE:
            index = 2

        earthquakes = self.__get_all_earthquakes()

        for earthquake in earthquakes:
            if self.__is_value_meet_rule(earthquake.intensity[index], rule):
                return earthquake

        return None

    def __is_value_meet_rule(self, value: float, rule: Rule) -> bool:
        if rule.operator == RuleOperator.EQUAL_TO:
            return value == rule.value
        elif rule.operator == RuleOperator.GREATER_THAN:
            return value > rule.value
        elif rule.operator == RuleOperator.GREATER_THAN_OR_EQUAL_TO:
            return value >= rule.value
        elif rule.operator == RuleOperator.LESS_THAN:
            return value < rule.value
        else:  # LESS_THAN_OR_EQUAL_TO
            return value <= rule.value

    def __create_issue_and_send_email(self, rule: Rule) -> bool:
        issue = self.issue_svc.create(rule)
        if issue is None:
            return False

        self.email_svc.send_noreply([rule.user.email], issue.title, issue.content)
        return True

    def trigger_over_threshold(
        self,
    ) -> None:
        rules = self.__get_all_enable_rules()

        for rule in rules:
            if self.is_reservoir(rule.position):
                dam = self.__first_reservoir_by_operator(
                    rule.position,
                    rule.resource,
                    rule.operator,
                    rule.value,
                    rule.last_triggered_by,
                )
                if dam is None:
                    continue

                notify_successfuly = self.__create_issue_and_send_email(rule)
                if not notify_successfuly:
                    continue

                rule.last_triggered_by = datetime.fromtimestamp(dam.timestamp)

            elif self.is_electricity(rule.position):
                power = self.__get_latest_eletricity()
                if power is None:
                    continue

                position_without_suffix = rule.position.replace(
                    RulePosition.ELECTRICITY_SUFFIX.value, ""
                )
                column = getattr(power, position_without_suffix.lower())
                if self.__is_value_meet_rule(column[rule.resource.lower()], rule):
                    notify_successfuly = self.__create_issue_and_send_email(rule)
                    if not notify_successfuly:
                        continue

                    rule.last_triggered_by = datetime.fromtimestamp(power.timestamp)

            elif self.is_earthquake(rule.position):
                earthquake = self.__first_earthquake_by_operator(rule)
                if earthquake is None:
                    continue

                notify_successfuly = self.__create_issue_and_send_email(rule)
                if not notify_successfuly:
                    continue

                rule.last_triggered_by = datetime.fromtimestamp(earthquake.timestamp)

            self.session.add(rule)

        self.session.commit()
