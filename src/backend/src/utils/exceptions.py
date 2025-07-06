class NotFoundException(Exception):
    """Raised when an element was not found"""
    def __init__(self, message="Not found"):
        self.message = message
        super().__init__(self.message)


class RequestValidationError(Exception):
    """Raised when validation for request failed"""
    pass
