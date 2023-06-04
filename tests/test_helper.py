import pytest
from fastapi import HTTPException, status

from meter.constant.response_code import ResponseCode
from meter.exception import CustomErrorException
from meter.helper import *


class TestHelperClass:
    def test_raise_not_found_exception(self):
        with pytest.raises(HTTPException) as excinfo:
            raise_not_found_exception()
        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

    def test_raise_custom_exception(self):
        with pytest.raises(CustomErrorException) as excinfo:
            raise_custom_exception(ResponseCode.RULE_CREATE_FAILED_1001)
        assert excinfo.value.response_code == ResponseCode.RULE_CREATE_FAILED_1001

    def test_get_message_by_response_code(self):
        message = get_message_by_response_code(ResponseCode.RULE_CREATE_FAILED_1001)
        assert message == Message.RULE_CREATE_FAILED_1001.value.__str__()

    def test_get_message_by_response_code_not_found(self, monkeypatch):
        monkeypatch.setattr(Message, "_member_names_", [])

        message = get_message_by_response_code(ResponseCode.RULE_CREATE_FAILED_1001)
        assert message == ResponseCode.RULE_CREATE_FAILED_1001.name.__str__()
