from typing import Optional
from pydantic import BaseModel
from dataAccess.database.database import ActionInterval
from endpoints.decorators.request_validator import GetRequestBaseModel, PostRequestBaseModel


class AddActionInterval(PostRequestBaseModel):
    date_minutes_start: int = 0
    date_minutes_end: Optional[int] = None
    allowed_time_minutes_start: Optional[int] = None
    allowed_time_minutes_end: Optional[int] = None

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
        existing_action_interval.date_minutes_end = self.date_minutes_end
        existing_action_interval.allowed_time_minutes_start = self.allowed_time_minutes_start
        existing_action_interval.allowed_time_minutes_end = self.allowed_time_minutes_end
        return existing_action_interval


class GetActionInterval(GetRequestBaseModel):
    id: int
    date_minutes_start: int
    date_minutes_end: Optional[int] = None
    allowed_time_minutes_start: Optional[int] = None
    allowed_time_minutes_end: Optional[int] = None

    @staticmethod
    def from_sql_model(action_interval: ActionInterval) -> "GetActionInterval":
        return GetActionInterval(
            id=action_interval.id,
            date_minutes_start=action_interval.date_minutes_start,
            date_minutes_end=action_interval.date_minutes_end,
            allowed_time_minutes_start=action_interval.allowed_time_minutes_start,
            allowed_time_minutes_end=action_interval.allowed_time_minutes_end
        )
