from datetime import timedelta, datetime
from typing import Optional
from pydantic import BaseModel

from database.database import Website, ActionInterval
from endpoints.decorators.get_request_validator import GetRequestBaseModel
from endpoints.models.action_interval_model import AddActionInterval, GetActionInterval
from endpoints.models.custom_access_model import AddCustomAccess, GetCustomAccess


class AddWebsite(BaseModel):
    url: str
    name: str
    username: str
    password: str
    pin: Optional[str] = None
    expiration_interval: Optional[timedelta] = None
    custom_access: Optional[AddCustomAccess] = None
    action_interval: Optional[AddActionInterval] = None

    def to_sql_model(self) -> Website:
        website = Website(
            url=self.url,
            name=self.name,
            username=self.username,
            password=self.password,
            pin=self.pin,
            added_at=datetime.now(),
            expiration_interval=self.expiration_interval,
        )
        if self.action_interval is not None:
            ai: AddActionInterval = self.action_interval
            action_interval = ActionInterval(
                interval_start=timedelta(days=ai.interval_start_days, hours=ai.interval_start_hours,
                                         minutes=ai.interval_start_minutes),
                interval_end=timedelta(days=ai.interval_end_days, hours=ai.interval_end_hours,
                                       minutes=ai.interval_end_minutes),
                interval_hours_min=ai.interval_hours_min,
                interval_hours_max=ai.interval_hours_max,
            )
            website.action_interval = action_interval
        return website


class GetWebsite(GetRequestBaseModel):
    id: int
    url: str
    name: str
    username: str
    password: str
    pin: Optional[str] = None
    expiration_interval: Optional[str] = None
    custom_access: Optional[GetCustomAccess] = None
    action_interval: Optional[GetActionInterval] = None

    @staticmethod
    def from_sql_model(website: Website) -> "GetWebsite":
        return GetWebsite(
            id=website.id,
            url=website.url,
            name=website.name,
            username=website.username,
            password=website.password,
            pin=website.pin,
            expiration_interval=str(website.expiration_interval),
            custom_access=GetCustomAccess.from_sql_model(website.custom_access) if website.custom_access else None,
            action_interval=GetActionInterval.from_sql_model(website.action_interval) if website.action_interval else None,
        )
