from typing import Optional
from pydantic import BaseModel
from dataAccess.database.database import ActionInterval
from endpoints.decorators.get_request_validator import GetRequestBaseModel


class AddActionInterval(BaseModel):
    date_minutes_start: int = 0
    date_minutes_end: int = 0
    allowed_time_minutes_start: int = 0
    allowed_time_minutes_end: int = 0

    def to_sql_model(self) -> ActionInterval:
        return ActionInterval(date_minutes_start=self.date_minutes_start,
                              date_minutes_end=self.date_minutes_end,
                              allowed_time_minutes_start=self.allowed_time_minutes_start,
                              allowed_time_minutes_end=self.allowed_time_minutes_end)

class EditActionInterval(BaseModel):
    date_minutes_start: Optional[int] = None
    date_minutes_end: Optional[int] = None
    allowed_time_minutes_start: Optional[int] = None
    allowed_time_minutes_end: Optional[int] = None

    def edit_existing_model(self, existing_action_interval: ActionInterval) -> ActionInterval:
        if self.date_minutes_start is not None:
            existing_action_interval.date_minutes_start = self.date_minutes_start
        if self.date_minutes_end is not None:
            existing_action_interval.date_minutes_end = self.date_minutes_end
        if self.allowed_time_minutes_start is not None:
            existing_action_interval.allowed_time_minutes_start = self.allowed_time_minutes_start
        if self.allowed_time_minutes_end is not None:
            existing_action_interval.allowed_time_minutes_end = self.allowed_time_minutes_end
        return existing_action_interval

class GetActionInterval(GetRequestBaseModel):
    id: int
    date_minutes_start: int
    date_minutes_end: int
    allowed_time_minutes_start: int
    allowed_time_minutes_end: int

    @staticmethod
    def from_sql_model(action_interval: ActionInterval) -> "GetActionInterval":
        return GetActionInterval(
            id=action_interval.id,
            date_minutes_start=action_interval.date_minutes_start,
            date_minutes_end=action_interval.date_minutes_end,
            allowed_time_minutes_start=action_interval.allowed_time_minutes_start,
            allowed_time_minutes_end=action_interval.allowed_time_minutes_end
        )