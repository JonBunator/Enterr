from datetime import datetime
from typing import List
from dataAccess.database.change_database import DataBase
from dataAccess.database.database import Website, ActionHistory, ActionFailedDetails, ActionStatusCode
from endpoints.models.action_history_model import AddManualActionHistory
from endpoints.models.website_model import AddWebsite, EditWebsite, DeleteWebsite
from endpoints.webhook_endpoints import WebhookEndpoints

class DataAccess:
    def __init__(self, webhook_endpoints: WebhookEndpoints):
        self.webhook_endpoints = webhook_endpoints

    @staticmethod
    def get_all_websites() -> List[Website]:
        return DataBase.get_all_websites()

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

    def add_action_history(self, website_id: int, action_history: ActionHistory):
        action_history_id = DataBase.add_action_history(website_id, action_history)
        self.webhook_endpoints.action_history_changed(action_history_id=action_history_id)
        return action_history_id

    def add_manual_action_history(self, action_history_request: AddManualActionHistory):
        action_history = action_history_request.to_sql_model()
        self.add_action_history(action_history_request.id, action_history)

    def action_history_finish_execution(self, action_history_id: int, execution_status: ActionStatusCode, failed_details: ActionFailedDetails, screenshot_id: str = None):
        DataBase.action_history_finish_execution(action_history_id, execution_status, failed_details, screenshot_id)
        self.webhook_endpoints.action_history_changed(action_history_id=action_history_id)

    def unexpected_execution_failure(self, website_id: int, execution_started: datetime):
        ids = DataBase.unexpected_execution_failure(website_id=website_id, execution_started=execution_started)
        for action_history_id in ids:
            self.webhook_endpoints.action_history_changed(action_history_id=action_history_id)

    @staticmethod
    def trigger_login(website_id):
        DataBase.trigger_login(website_id=website_id)

    @staticmethod
    def get_action_history(website: Website) -> List[ActionHistory]:
        return DataBase.get_action_history(website)