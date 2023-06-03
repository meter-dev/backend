from enum import Enum

from meter.constant.response_code import *


class Message(Enum):
    RULE_CREATE_FAILED_1001 = "Create failed."
    RULE_UPDATE_FAILED_1002 = "Update failed."
    RULE_DELETE_FAILED_1003 = "Delete failed."
    RULE_ENABLE_FAILED_1004 = "Enable failed."
    RULE_DISABLE_FAILED_1005 = "Disable failed."
    RULE_TRIGGER_FAILED_1006 = "Trigger failed."
