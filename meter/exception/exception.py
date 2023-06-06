from fastapi import status

from meter.constant.response_code import ResponseCode


class CustomErrorException(Exception):
    def __init__(
        self,
        response_code: ResponseCode,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.response_code = response_code
        self.status_code = status_code
