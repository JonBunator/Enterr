from typing import List
from dataAccess.database.change_database import DataBase
from dataAccess.database.database import (
    Website,
    ActionHistory,
    User,
)
from endpoints.models.action_history_model import AddManualActionHistory
from endpoints.models.website_model import AddWebsite, EditWebsite, DeleteWebsite
from endpoints.webhook_endpoints import WebhookEndpoints


class DataAccess:
    def __init__(self, webhook_endpoints: WebhookEndpoints):
        self.webhook_endpoints = webhook_endpoints

    @staticmethod
    def get_current_user() -> User:
        return DataBase.get_current_user()

    @staticmethod
    def get_websites() -> List[Website]:
        return DataBase.get_websites()

    @staticmethod
    def get_website(website_id: int) -> Website:
        return DataBase.get_website(website_id)

    def add_website(self, request: AddWebsite):
        website = request.to_sql_model()
        DataBase.add_website(website)
        self.webhook_endpoints.login_data_changed()

    def edit_website(self, request: EditWebsite):
        existing_website = DataBase.get_website(request.id)
        website = request.edit_existing_model(existing_website)
        DataBase.edit_website(website)
        self.webhook_endpoints.login_data_changed()

    def delete_website(self, request: DeleteWebsite):
        website = DataBase.get_website(request.id)
        DataBase.delete_website(website)
        self.webhook_endpoints.login_data_changed()

    def add_manual_action_history(self, action_history_request: AddManualActionHistory):
        action_history = action_history_request.to_sql_model()
        DataBase.add_manual_action_history(action_history_request.id, action_history)
        self.webhook_endpoints.action_history_changed(
            action_history_id=action_history.id
        )

    @staticmethod
    def trigger_login(website_id):
        DataBase.trigger_login(website_id=website_id)

    @staticmethod
    def get_action_history(website_id: int) -> List[ActionHistory]:
        return DataBase.get_action_history(website_id)

    @staticmethod
    def get_user(username: str):
        return DataBase.get_user(username)
