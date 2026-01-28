from datetime import datetime
from typing import List

from dataAccess.database.change_database import DataBase
from dataAccess.database.database import (
    Website, ActionHistory, ActionStatusCode, ActionFailedDetails, Notification, )
from endpoints.webhooks.webhook_endpoints import WebhookEndpoints


class DataAccessInternal:
    """
    Internal data access class that should only be called internally and not by the user.
    """
    def __init__(self, webhook_endpoints: WebhookEndpoints):
        self.webhook_endpoints = webhook_endpoints

    @staticmethod
    def get_website_by_id(website_id: int) -> Website:
        return DataBase.get_website_by_id(website_id)

    @staticmethod
    def get_websites_all_users() -> List[Website]:
        return DataBase.get_websites_all_users()

    @staticmethod
    def get_website_all_users(website_id: int) -> Website:
        return DataBase.get_website_all_users(website_id)

    def unexpected_execution_failure(
        self, website_id: int, execution_started: datetime
    ):
        ids = DataBase.unexpected_execution_failure(
            website_id=website_id, execution_started=execution_started
        )

        for action_history_id in ids:
            self.webhook_endpoints.action_history_changed(
                action_history_id=action_history_id
            )


    def add_action_history(self, website_id: int, action_history: ActionHistory):
        created_action_history = DataBase.add_action_history(website_id, action_history)

        self.webhook_endpoints.action_history_changed(
            action_history_id=created_action_history.id
        )

        return created_action_history.id

    def action_history_finish_execution(
        self,
        action_history_id: int,
        execution_status: ActionStatusCode,
        failed_details: ActionFailedDetails,
        custom_failed_details_message: str = None,
        screenshot_id: str = None,
    ):
        DataBase.action_history_finish_execution(
            action_history_id, execution_status, failed_details, custom_failed_details_message, screenshot_id
        )

        self.webhook_endpoints.action_history_changed(
            action_history_id=action_history_id
        )


    @staticmethod
    def get_notifications_all_users() -> List[Notification]:
        return DataBase.get_notifications_all_users()

    @staticmethod
    def get_notifications_for_user(action_history: ActionHistory) -> List[Notification]:
        return DataBase.get_notifications_for_user(action_history)
