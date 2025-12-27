from execution.login.constants import LoginStatusCode


class NotFoundException(Exception):
    """Raised when an element was not found"""

    def __init__(self, message="Not found"):
        super().__init__(message)
        self.message = message


class ScriptExecutionStopped(Exception):
    """Raised when exception occurred in script execution of custom login"""

    def __init__(self, status: LoginStatusCode = LoginStatusCode.UNKNOWN_EXECUTION_ERROR,
                 message="Error while executing custom login script"):
        super().__init__(message)
        self.status = status
        self.message = message


class RequestValidationError(Exception):
    """Raised when validation for request failed"""
    pass
