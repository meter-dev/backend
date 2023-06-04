from fastapi import HTTPException, status

from meter.constant.message import Message
from meter.constant.response_code import ResponseCode
from meter.exception import CustomErrorException


def raise_not_found_exception():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def raise_custom_exception(response_code: ResponseCode):
    raise CustomErrorException(response_code)


def get_message_by_response_code(response_code: ResponseCode) -> str:
    if not response_code.name in Message._member_names_:
        return response_code.name.__str__()
    return Message[response_code.name].value.__str__()
