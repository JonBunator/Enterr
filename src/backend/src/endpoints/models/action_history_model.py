from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from dataAccess.database.database import ActionHistory
from utils.utils import to_utc_time
from endpoints.decorators.request_validator import GetRequestBaseModel


class GetActionHistory(GetRequestBaseModel):
    id: int
    execution_started: datetime
    execution_ended: Optional[datetime]
    execution_status: str
    failed_details: Optional[str]
    custom_failed_details_message: Optional[str]
    screenshot_id: Optional[str]

    @staticmethod
    def from_sql_model(action_history: ActionHistory) -> "GetActionHistory":
        return GetActionHistory(
            id=action_history.id,
            execution_started=to_utc_time(action_history.execution_started),
            execution_ended=to_utc_time(action_history.execution_ended),
            execution_status=action_history.execution_status.value,
            failed_details=(
                action_history.failed_details.value
                if action_history.failed_details
                else None
            ),
            custom_failed_details_message=(
                action_history.custom_failed_details_message
            ),
            screenshot_id=action_history.screenshot_id,
        )


class GetLastSuccessfulLogin(BaseModel):
    action_history: Optional[GetActionHistory]
