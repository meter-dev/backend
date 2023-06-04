from meter.constant import ExtendedEnum


class IssueStatus(ExtendedEnum):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    SOLVED = "SOLVED"
