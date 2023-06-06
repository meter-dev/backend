from meter.constant import ExtendedEnum
from meter.constant.response_code import *


class Message(ExtendedEnum):
    RULE_CREATE_FAILED_1001 = "Create failed."
    RULE_UPDATE_FAILED_1002 = "Update failed."
    RULE_DELETE_FAILED_1003 = "Delete failed."
    RULE_ENABLE_FAILED_1004 = "Enable failed."
    RULE_DISABLE_FAILED_1005 = "Disable failed."
    RULE_TRIGGER_FAILED_1006 = "Trigger failed."

    ISSUE_UPDATE_FAILED_1101 = "Update failed."
    ISSUE_DELETE_FAILED_1102 = "Delete failed."
