class RestroomError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class RestroomInvalidFieldError(RestroomError):
    pass


class RestroomInvalidHTTPMethodError(RestroomError):
    pass


class RestroomInvalidOperatorError(RestroomError):
    pass


class RestroomMalformedFilterError(RestroomError):
    pass
