class CustomException(Exception):
    message = ""

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class BadRequestException(CustomException):
    def __init__(self, message):
        super().__init__(message=message)
