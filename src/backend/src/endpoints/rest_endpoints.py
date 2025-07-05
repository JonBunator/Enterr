import os
from http import HTTPStatus
from typing import List

from fastapi import FastAPI
from pydantic import ValidationError

from dataAccess.data_access import DataAccess
from dataAccess.database.database import engine
from endpoints.decorators.get_request_validator import validate_get_request
from endpoints.decorators.post_request_validator import CustomValidationError
from endpoints.models.action_history_model import (
    GetActionHistory,
    AddManualActionHistory,
)
from endpoints.models.api_response_model import ApiGetResponse, ApiPostResponse
from endpoints.models.notification_model import AddNotification, GetNotification, DeleteNotification, EditNotification
from endpoints.models.other_model import TriggerAutomaticLogin
from endpoints.models.user_login_model import UserLogin, GetUserData
from endpoints.models.website_model import (
    GetWebsite,
    AddWebsite,
    EditWebsite,
    DeleteWebsite,
)
from execution.notifications.notification_manager import NotificationManager


def register_rest_endpoints(app: FastAPI, data_access: DataAccess, notification_manager: NotificationManager):
    @app.get("/api/websites", response_model=List[GetWebsite])
    @validate_get_request(GetWebsite)
    def get_websites():
        return DataAccess.get_websites()

    @app.get("/api/websites/<int:website_id>", response_model=GetWebsite)
    @validate_get_request(GetWebsite)
    def get_website(website_id: int):
        return DataAccess.get_website(website_id)

    @app.post("/api/websites/add")
    def add_website(website_request: AddWebsite):
        data_access.add_website(website_request)

    @app.post("/api/websites/edit")
    def edit_website(website_request: EditWebsite):
        data_access.edit_website(website_request)

    @app.post("/api/websites/delete")
    def delete_website(website_request: DeleteWebsite):
        data_access.delete_website(website_request)

    @app.post("/api/action_history/<int:website_id>")
    def get_action_history(website_id: int):
        return DataAccess.get_action_history(website_id)

    @app.post("/api/action_history/manual_add")
    def add_manual_action_history(action_history_request: AddManualActionHistory):
        data_access.add_manual_action_history(action_history_request)

    @app.post("/api/trigger_login")
    def trigger_login(login_request: TriggerAutomaticLogin):
        DataAccess.trigger_login(login_request.id)

    @app.post("/api/notifications/add")
    def add_notification(notification_request: AddNotification):
        data_access.add_notification(notification_request)

    @app.post("/api/notifications/test")
    def test_notification(notification_request: AddNotification):
        notification_manager.test_notification(notification_request.to_sql_model())

    @app.post("/api/notifications/edit")
    def edit_notification(notification_request: EditNotification):
        data_access.edit_notification(notification_request)

    @app.post("/api/notifications/delete")
    def delete_notification(notification_request: DeleteNotification):
        data_access.delete_notification(notification_request)

    @app.get("/api/notifications", response_model=List[GetNotification])
    @validate_get_request(GetNotification)
    def get_notifications():
        return DataAccess.get_notifications()

    @app.post("/api/user/login")
    def login(login_request: UserLogin):
        user = data_access.get_user(login_request.username)
        if user and user.check_password(login_request.password):
            print("valid")
        else:
            raise CustomValidationError("Invalid username or password")


    """
    @app.post("/api/user/logout")
    def logout():
        logout_user()
    """

    @app.get("/api/user/data", response_model=GetUserData)
    @validate_get_request(GetUserData)
    def get_user_data():
        return DataAccess.get_current_user()

    """
    @app.get("/api/screenshot/<string:screenshot_id>")
    def get_screenshot(screenshot_id: str):
        dev_mode = os.getenv("FLASK_ENV") != "production"
        if dev_mode:
            path = f"../config/images"
        else:
            path = f"/config/images"
        image_path = os.path.join(path, f"{screenshot_id}.png")

        try:
            if os.path.isfile(image_path):
                return send_file(image_path, mimetype="image/png")
            else:
                response = ApiGetResponse(
                    success=False, message="Image not found", error=""
                )
                return jsonify(response.model_dump()), HTTPStatus.NOT_FOUND
        except Exception as e:
            # Handle general exceptions and return a 500 Internal Server Error response
            response = ApiGetResponse(
                success=False, message="An error occurred", error=str(e)
            )
            return jsonify(response.model_dump()), HTTPStatus.INTERNAL_SERVER_ERROR
    """