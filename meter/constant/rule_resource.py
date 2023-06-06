from meter.constant import ExtendedEnum


class RuleResource(ExtendedEnum):
    # Reservoir
    STORAGE = "STORAGE"
    PERCENT = "PERCENT"

    # Electricity
    LOAD = "LOAD"
    MAX_SUPPLY = "MAX_SUPPLY"
    RECV_RATE = "RECV_RATE"

    # Earthquake
    INTENSITY = "INTENSITY"
