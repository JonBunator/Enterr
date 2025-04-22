from dataAccess.database.database import Notification
from endpoints.decorators.post_request_validator import PostRequestBaseModel


class AddNotification(PostRequestBaseModel):
    apprise_token: str
    title: str
    body: str
    trigger: str

    def to_sql_model(self) -> Notification:
        return Notification(
            apprise_token=self.apprise_token,
            title=self.title,
            body=self.body,
            trigger=self.trigger,
        )
