from typing import List, Annotated

from fastapi import Depends

from dataAccess.database.change_database import DataBase, oauth2_scheme
from dataAccess.database.database import (
    Website,
    ActionHistory,
    User,
    Notification,
)
from endpoints.models.action_history_model import AddManualActionHistory
from endpoints.models.notification_model import (
    AddNotification,
    EditNotification,
    DeleteNotification,
)
from endpoints.models.website_model import AddWebsite, EditWebsite, DeleteWebsite, CheckCustomLoginScript, \
    CheckCustomLoginScriptResponse
from endpoints.webhooks.webhook_endpoints import WebhookEndpoints
from execution.login.custom_login.parser import CustomLoginScriptParser


class DataAccess:
    def __init__(self, webhook_endpoints: WebhookEndpoints):
        self.webhook_endpoints = webhook_endpoints

    @staticmethod
    def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
        return DataBase.get_current_user(token)

    @staticmethod
    def get_websites(current_user: User) -> List[Website]:
        return DataBase.get_websites(current_user)

    @staticmethod
    def get_website(website_id: int, current_user: User) -> Website:
        return DataBase.get_website(website_id, current_user)

    @staticmethod
    def check_custom_login_script(request: CheckCustomLoginScript) -> CheckCustomLoginScriptResponse:
        error = CustomLoginScriptParser.check_syntax(request.script)
        return CheckCustomLoginScriptResponse(error=error)

    def add_website(self, request: AddWebsite, current_user: User):
        website = request.to_sql_model()
        DataBase.add_website(website, current_user)
        self.webhook_endpoints.login_data_changed()

    def edit_website(self, request: EditWebsite, current_user: User):
        existing_website = DataBase.get_website(request.id, current_user)
        website = request.edit_existing_model(existing_website)
        DataBase.edit_website(website, current_user)
        self.webhook_endpoints.login_data_changed()

    def delete_website(self, request: DeleteWebsite, current_user: User):
        DataBase.delete_website(request.id, current_user)
        self.webhook_endpoints.login_data_changed()

    def add_manual_action_history(
        self, action_history_request: AddManualActionHistory, current_user: User
    ):
        action_history = action_history_request.to_sql_model()
        DataBase.add_manual_action_history(
            action_history_request.id, action_history, current_user
        )
        self.webhook_endpoints.action_history_changed(
            action_history_id=action_history.id
        )

    def add_notification(self, request: AddNotification, current_user: User):
        notification = request.to_sql_model()
        DataBase.add_notification(notification, current_user)
        self.webhook_endpoints.notifications_changed()

    def edit_notification(self, request: EditNotification, current_user: User):
        existing_notification = DataBase.get_notification(request.id, current_user)
        notification = request.edit_existing_model(existing_notification)
        DataBase.edit_notification(notification, current_user)
        self.webhook_endpoints.notifications_changed()

    def delete_notification(self, request: DeleteNotification, current_user: User):
        notification = DataBase.get_notification(request.id, current_user)
        DataBase.delete_notification(notification, current_user)
        self.webhook_endpoints.notifications_changed()

    @staticmethod
    def trigger_login(website_id, current_user: User):
        DataBase.trigger_login(website_id, current_user)

    @staticmethod
    def get_action_history(website_id: int, current_user: User) -> List[ActionHistory]:
        return DataBase.get_action_history(website_id, current_user)

    @staticmethod
    def get_user(username: str):
        return DataBase.get_user(username)

    @staticmethod
    def get_notifications(current_user: User) -> List[Notification]:
        return DataBase.get_notifications(current_user)
