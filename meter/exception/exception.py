from meter.constant.response_code import ResponseCode


class CustomErrorException(Exception):
    def __init__(self, response_code: ResponseCode):
        self.response_code = response_code
