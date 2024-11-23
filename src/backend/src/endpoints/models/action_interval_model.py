from pydantic import BaseModel
from database.database import ActionInterval
from endpoints.decorators.get_request_validator import GetRequestBaseModel


class AddActionInterval(BaseModel):
    interval_start_days: int = 0
    interval_start_hours: int = 0
    interval_start_minutes: int = 0
    interval_end_days: int = 0
    interval_end_hours: int = 0
    interval_end_minutes: int = 0
    interval_hours_min: int = 0
    interval_hours_max: int = 24

class GetActionInterval(GetRequestBaseModel):
    id: int
    interval_start_days: int
    interval_start_hours: int
    interval_start_minutes: int
    interval_end_days: int
    interval_end_hours: int
    interval_end_minutes: int
    interval_hours_min: int
    interval_hours_max: int

    @staticmethod
    def from_sql_model(action_interval: ActionInterval) -> "GetActionInterval":
        interval_start_days = action_interval.interval_start.days
        interval_start_seconds = action_interval.interval_start.seconds
        interval_start_hours, remainder = divmod(interval_start_seconds, 3600)
        interval_start_minutes = remainder // 60

        interval_end_days = action_interval.interval_end.days
        interval_end_seconds = action_interval.interval_end.seconds
        interval_end_hours, remainder = divmod(interval_end_seconds, 3600)
        interval_end_minutes = remainder // 60

        return GetActionInterval(
            id=action_interval.id,
            interval_start_days=interval_start_days,
            interval_start_hours=interval_start_hours,
            interval_start_minutes=interval_start_minutes,
            interval_end_days=interval_end_days,
            interval_end_hours=interval_end_hours,
            interval_end_minutes=interval_end_minutes,
            interval_hours_min=action_interval.interval_hours_min,
            interval_hours_max=action_interval.interval_hours_max,
        )