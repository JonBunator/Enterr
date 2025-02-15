from datetime import datetime, timezone
from typing import Optional
from dataAccess.database.database import ActionHistory, ActionStatusCode
from endpoints.decorators.get_request_validator import GetRequestBaseModel
from endpoints.decorators.post_request_validator import PostRequestBaseModel


class GetActionHistory(GetRequestBaseModel):
    id: int
    execution_started: datetime
    execution_ended: Optional[datetime]
    execution_status: str
    failed_details: Optional[str]
    screenshot_id: Optional[str]

    @staticmethod
    def from_sql_model(action_history: ActionHistory) -> "GetActionHistory":
        return GetActionHistory(
            id=action_history.id,
            execution_started=action_history.execution_started,
            execution_ended=action_history.execution_ended,
            execution_status=action_history.execution_status.value,
            failed_details=action_history.failed_details.value if action_history.failed_details else None,
            screenshot_id=action_history.screenshot_id
        )


class AddManualActionHistory(PostRequestBaseModel):
    id: int

    def to_sql_model(self) -> ActionHistory:
        return ActionHistory(
            execution_started=datetime.now(timezone.utc),
            execution_ended=datetime.now(timezone.utc),
            execution_status=ActionStatusCode.SUCCESS,
        )
