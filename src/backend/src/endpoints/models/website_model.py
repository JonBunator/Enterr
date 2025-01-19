from datetime import timedelta, datetime, timezone
from typing import Optional
from pydantic import BaseModel

from dataAccess.database.database import Website, CustomAccess
from endpoints.decorators.get_request_validator import GetRequestBaseModel
from endpoints.decorators.post_request_validator import PostRequestBaseModel
from endpoints.models.action_interval_model import AddActionInterval, GetActionInterval, EditActionInterval
from endpoints.models.custom_access_model import AddCustomAccess, GetCustomAccess, EditCustomAccess
from utils.utils import timedelta_to_parts

class DateTime(BaseModel):
    day: Optional[int] = None
    month: Optional[int] = None
    year: Optional[int] = None
    hour: Optional[int] = None
    minute: Optional[int] = None

    @staticmethod
    def from_datetime(dt: datetime) -> "DateTime":
        return DateTime(
            day=dt.day,
            month=dt.month,
            year=dt.year,
            hour=dt.hour,
            minute=dt.minute
        )

class AddWebsite(PostRequestBaseModel):
    url: str
    success_url: str
    name: str
    username: str
    password: str
    pin: Optional[str] = None
    take_screenshot: bool
    paused: Optional[bool] = None
    expiration_interval_minutes: Optional[int] = None
    custom_access: Optional[AddCustomAccess] = None
    action_interval: AddActionInterval

    def to_sql_model(self) -> Website:
        expiration_interval = None
        if self.expiration_interval_minutes is not None:
            expiration_interval = timedelta(minutes=self.expiration_interval_minutes)
        website = Website(
            url=self.url,
            success_url=self.success_url,
            name=self.name,
            username=self.username,
            password=self.password,
            pin=self.pin if self.pin != '' else None,
            take_screenshot=self.take_screenshot,
            paused=self.paused if self.paused is not None else False,
            added_at=datetime.now(timezone.utc),
            expiration_interval=expiration_interval,
        )
        if self.custom_access is not None:
            website.custom_access = self.custom_access.to_sql_model()

        website.action_interval = self.action_interval.to_sql_model()
        return website

class EditWebsite(BaseModel):
    id: int
    url: Optional[str] = None
    success_url: Optional[str] = None
    name: Optional[str] = None
    username:Optional[str] = None
    password: Optional[str] = None
    pin: Optional[str] = None
    take_screenshot: Optional[bool] = None
    paused: Optional[bool] = None
    expiration_interval_minutes: Optional[int] = None
    custom_access: Optional[EditCustomAccess] = None
    action_interval: Optional[EditActionInterval] = None

    def edit_existing_model(self, existing_website: Website) -> Website:
        if self.url is not None:
            existing_website.url = self.url
        if self.success_url is not None:
            existing_website.success_url = self.success_url
        if self.name is not None:
            existing_website.name = self.name
        if self.username is not None:
            existing_website.username = self.username
        if self.password is not None:
            existing_website.password = self.password
        if self.pin is not None:
            existing_website.pin = self.pin
        if self.take_screenshot is not None:
            existing_website.take_screenshot = self.take_screenshot
        if self.paused is not None:
            existing_website.paused = self.paused
        if self.expiration_interval_minutes is not None:
            existing_website.expiration_interval = timedelta(minutes=self.expiration_interval_minutes)
        else:
            existing_website.expiration_interval = None
        if self.custom_access is not None:
            existing_website.custom_access = CustomAccess(username_xpath=self.custom_access.username_xpath,
                                                          password_xpath=self.custom_access.password_xpath,
                                                          pin_xpath=self.custom_access.pin_xpath,
                                                          submit_button_xpath=self.custom_access.submit_button_xpath)
        else:
            existing_website.custom_access = None
        if self.action_interval is not None:
            existing_website.action_interval = self.action_interval.edit_existing_model(existing_website.action_interval)

        if self.paused:
            existing_website.next_schedule = None
        else:
            existing_website.next_schedule = existing_website.action_interval.get_random_action_datetime()

        return existing_website

class DeleteWebsite(BaseModel):
    id: int

class GetWebsite(GetRequestBaseModel):
    id: int
    url: str
    success_url: str
    name: str
    username: str
    password: str
    pin: Optional[str] = None
    take_screenshot: bool
    paused: bool
    expiration_interval_minutes: Optional[int] = None
    custom_access: Optional[GetCustomAccess] = None
    action_interval: Optional[GetActionInterval] = None
    next_schedule: Optional[datetime] = None

    @staticmethod
    def from_sql_model(website: Website) -> "GetWebsite":
        if website.expiration_interval is None:
            expiration_interval_minutes = None
        else:
            expiration_interval_parts = timedelta_to_parts(website.expiration_interval)
            expiration_interval_minutes = expiration_interval_parts.days * 24 * 60 + expiration_interval_parts.hours * 60 + expiration_interval_parts.minutes

        return GetWebsite(
            id=website.id,
            url=website.url,
            success_url=website.success_url,
            name=website.name,
            username=website.username,
            password=website.password,
            pin=website.pin,
            take_screenshot=website.take_screenshot,
            paused=website.paused,
            expiration_interval_minutes=expiration_interval_minutes,
            custom_access=GetCustomAccess.from_sql_model(website.custom_access) if website.custom_access else None,
            action_interval=GetActionInterval.from_sql_model(website.action_interval) if website.action_interval else None,
            next_schedule=website.next_schedule,
        )
