from datetime import timedelta, datetime
from typing import Optional
from pydantic import BaseModel

from database.database import Website, ActionInterval, CustomAccess


class AddCustomAccess(BaseModel):
    username_xpath: str
    password_xpath: str
    pin_xpath: Optional[str] = None
    submit_button_xpath: str


class GetCustomAccess(BaseModel):
    id: int
    username_xpath: str
    password_xpath: str
    pin_xpath: Optional[str] = None
    submit_button_xpath: str

    @staticmethod
    def from_sql_model(custom_access: CustomAccess) -> "AddCustomAccess":
        return GetCustomAccess(
            id=custom_access.id,
            username_xpath=custom_access.username_xpath,
            password_xpath=custom_access.password_xpath,
            pin_xpath=custom_access.pin_xpath,
            submit_button_xpath=custom_access.submit_button_xpath,
        )

class AddActionInterval(BaseModel):
    interval_start_days: int = 0
    interval_start_hours: int = 0
    interval_start_minutes: int = 0
    interval_end_days: int = 0
    interval_end_hours: int = 0
    interval_end_minutes: int = 0
    interval_hours_min: int = 0
    interval_hours_max: int = 24

class GetActionInterval(BaseModel):
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


class GetWebsite(BaseModel):
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
