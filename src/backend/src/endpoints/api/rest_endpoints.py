from fastapi import FastAPI
from dataAccess.data_access import DataAccess
from execution.notifications.notification_manager import NotificationManager
from endpoints.api.website_endpoints import register_website_endpoints
from endpoints.api.action_history_endpoints import register_action_history_endpoints
from endpoints.api.notification_endpoints import register_notification_endpoints
from endpoints.api.user_endpoints import register_user_endpoints
from endpoints.api.utility_endpoints import register_utility_endpoints


def register_rest_endpoints(
    app: FastAPI, data_access: DataAccess, notification_manager: NotificationManager
):
    """Register all REST API endpoints by importing from thematic sub-files."""
    register_website_endpoints(app, data_access)
    register_action_history_endpoints(app, data_access)
    register_notification_endpoints(app, data_access, notification_manager)
    register_user_endpoints(app, data_access)
    register_utility_endpoints(app)
