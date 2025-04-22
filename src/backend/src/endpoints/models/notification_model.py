from typing import List

from dataAccess.database.database import Notification, ActionStatusCode
from endpoints.decorators.get_request_validator import GetRequestBaseModel
from endpoints.decorators.post_request_validator import PostRequestBaseModel


class AddNotification(PostRequestBaseModel):
    apprise_token: str
    title: str
    body: str
    triggers: List[str]

    def to_sql_model(self) -> Notification:
        return Notification(
            apprise_token=self.apprise_token,
            title=self.title,
            body=self.body,
            triggers=[ActionStatusCode(trigger) for trigger in self.triggers],
        )


class GetNotification(GetRequestBaseModel):
    apprise_token: str
    title: str
    body: str
    triggers: List[str]

    @staticmethod
    def from_sql_model(notification: Notification) -> "GetNotification":
        return GetNotification(
            apprise_token=notification.apprise_token,
            title=notification.title,
            body=notification.body,
            triggers=[trigger.value for trigger in notification.triggers],
        )