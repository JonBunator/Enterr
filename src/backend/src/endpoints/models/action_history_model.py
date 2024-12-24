from datetime import datetime
from typing import Optional
from dataAccess.database.database import ActionHistory
from endpoints.decorators.get_request_validator import GetRequestBaseModel


class GetActionHistory(GetRequestBaseModel):
    id: int
    execution_started: datetime
    execution_ended: Optional[datetime]
    execution_status: str
    failed_details: Optional[str]

    @staticmethod
    def from_sql_model(action_history: ActionHistory) -> "GetActionHistory":
        print(action_history)
        return GetActionHistory(
            id=action_history.id,
            execution_started=action_history.execution_started,
            execution_ended=action_history.execution_ended,
            execution_status=action_history.execution_status.value,
            failed_details=action_history.failed_details.value if action_history.failed_details else None,
        )
