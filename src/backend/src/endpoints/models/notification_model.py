from typing import List, Optional

from pydantic import BaseModel

from dataAccess.database.database import Notification, ActionStatusCode
from endpoints.decorators.request_validator import GetRequestBaseModel, PostRequestBaseModel


class AddNotification(PostRequestBaseModel):
    name: str
    apprise_token: str
    title: str
    body: str
    triggers: List[str]

    def to_sql_model(self) -> Notification:
        return Notification(
            name=self.name,
            apprise_token=self.apprise_token,
            title=self.title,
            body=self.body,
            triggers=[ActionStatusCode(trigger) for trigger in self.triggers],
        )


class EditNotification(BaseModel):
    name: Optional[str] = None
    apprise_token: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    triggers: Optional[List[str]] = None

    def edit_existing_model(self, existing_notification: Notification) -> Notification:
        if self.name is not None:
            existing_notification.name = self.name
        if self.apprise_token is not None:
            existing_notification.apprise_token = self.apprise_token
        if self.title is not None:
            existing_notification.title = self.title
        if self.body is not None:
            existing_notification.body = self.body
        if self.triggers is not None:
            existing_notification.triggers = [ActionStatusCode(trigger) for trigger in self.triggers]

        return existing_notification


class GetNotification(GetRequestBaseModel):
    id: int
    name: str
    apprise_token: str
    title: str
    body: str
    triggers: List[str]

    @staticmethod
    def from_sql_model(notification: Notification) -> "GetNotification":
        return GetNotification(
            id=notification.id,
            name=notification.name,
            apprise_token=notification.apprise_token,
            title=notification.title,
            body=notification.body,
            triggers=[trigger.value for trigger in notification.triggers],
        )
