from enum import Enum

from dataAccess.database.database import ActionStatusCode, ActionFailedDetails


class LoginStatusCode(Enum):
    SUCCESS = ActionStatusCode.SUCCESS
    AUTOMATIC_FORM_DETECTION_FAILED = (
        ActionFailedDetails.AUTOMATIC_FORM_DETECTION_FAILED
    )
    USERNAME_FIELD_NOT_FOUND = ActionFailedDetails.USERNAME_FIELD_NOT_FOUND
    PASSWORD_FIELD_NOT_FOUND = ActionFailedDetails.PASSWORD_FIELD_NOT_FOUND
    PIN_FIELD_NOT_FOUND = ActionFailedDetails.PIN_FIELD_NOT_FOUND
    SUBMIT_BUTTON_NOT_FOUND = ActionFailedDetails.SUBMIT_BUTTON_NOT_FOUND
    BUTTON_NOT_FOUND = ActionFailedDetails.BUTTON_NOT_FOUND
    TEXT_FIELD_NOT_FOUND = ActionFailedDetails.TEXT_FIELD_NOT_FOUND
    SUCCESS_URL_DID_NOT_MATCH = ActionFailedDetails.SUCCESS_URL_DID_NOT_MATCH
    UNKNOWN_EXECUTION_ERROR = ActionFailedDetails.UNKNOWN_EXECUTION_ERROR
    FAILED = ActionStatusCode.FAILED


TIMEOUT = 30

type CustomFailedDetailsMessage = str | None