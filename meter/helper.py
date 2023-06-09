from fastapi import HTTPException, status

from meter.constant.message import Message
from meter.constant.response_code import ResponseCode
from meter.exception import CustomErrorException


def raise_not_found_exception():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def raise_unauthorized_exception():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def raise_custom_exception(response_code: ResponseCode, status_code: int | None = None):
    args = {
        k: v
        for k, v in [
            ("response_code", response_code),
            ("status_code", status_code),
        ]
        if v is not None
    }
    raise CustomErrorException(**args)


def get_message_by_response_code(response_code: ResponseCode) -> str:
    if not response_code.name in Message._member_names_:
        return response_code.name.__str__()
    return Message[response_code.name].value.__str__()


def get_formatted_string_from_template(path: str, **kwargs) -> str:
    with open(path, "r") as f:
        template = f.read()
    return template.format(**kwargs)
