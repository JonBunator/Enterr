import os
from typing import List
from fastapi import FastAPI
from starlette.responses import FileResponse
from dataAccess.data_access import DataAccess
from dataAccess.database.database import get_session
from endpoints.decorators.request_validator import validate_request
from endpoints.models.action_history_model import (
    AddManualActionHistory, GetActionHistory,
)
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
from utils.exceptions import NotFoundException, RequestValidationError


def register_rest_endpoints(app: FastAPI, data_access: DataAccess, notification_manager: NotificationManager):
    @app.get("/api/websites", response_model=List[GetWebsite])
    @validate_request()
    def get_websites():
        with get_session() as session:
            websites = DataAccess.get_websites(session)
            return [GetWebsite.from_sql_model(d) for d in websites]

    @app.get("/api/websites/{website_id}", response_model=GetWebsite)
    @validate_request()
    def get_website(website_id: int):
        with get_session() as session:
            website = DataAccess.get_website(website_id, session)
            return GetWebsite.from_sql_model(website)

    @app.post("/api/websites/add")
    @validate_request()
    def add_website(website_request: AddWebsite):
        data_access.add_website(website_request)

    @app.post("/api/websites/edit")
    @validate_request()
    def edit_website(website_request: EditWebsite):
        data_access.edit_website(website_request)

    @app.post("/api/websites/delete")
    @validate_request()
    def delete_website(website_request: DeleteWebsite):
        data_access.delete_website(website_request)

    @app.get("/api/action_history/{website_id}", response_model=List[GetActionHistory])
    @validate_request()
    def get_action_history(website_id: int):
        with get_session() as session:
            action_histories = DataAccess.get_action_history(website_id, session)
            return [GetActionHistory.from_sql_model(d) for d in action_histories]

    @app.post("/api/action_history/manual_add")
    @validate_request()
    def add_manual_action_history(action_history_request: AddManualActionHistory):
        data_access.add_manual_action_history(action_history_request)

    @app.post("/api/trigger_login")
    @validate_request()
    def trigger_login(login_request: TriggerAutomaticLogin):
        DataAccess.trigger_login(login_request.id)

    @app.post("/api/notifications/add")
    @validate_request()
    def add_notification(notification_request: AddNotification):
        data_access.add_notification(notification_request)

    @app.post("/api/notifications/test")
    @validate_request()
    def test_notification(notification_request: AddNotification):
        notification_manager.test_notification(notification_request.to_sql_model())

    @app.post("/api/notifications/edit")
    @validate_request()
    def edit_notification(notification_request: EditNotification):
        data_access.edit_notification(notification_request)

    @app.post("/api/notifications/delete")
    @validate_request()
    def delete_notification(notification_request: DeleteNotification):
        data_access.delete_notification(notification_request)

    @app.get("/api/notifications", response_model=List[GetNotification])
    @validate_request()
    def get_notifications():
        with get_session() as session:
            notifications = DataAccess.get_notifications(session)
            return [GetNotification.from_sql_model(d) for d in notifications]

    @app.post("/api/user/login")
    @validate_request()
    def login(login_request: UserLogin):
        with get_session() as session:
            user = data_access.get_user(login_request.username, session)
            if user and user.check_password(login_request.password):
                print("valid")
            else:
                raise RequestValidationError("Invalid username or password")

    """
    @app.post("/api/user/logout")
    def logout():
        logout_user()
    """

    @app.get("/api/user/data", response_model=GetUserData)
    @validate_request()
    def get_user_data():
        with get_session() as session:
            return DataAccess.get_current_user(session)

    @app.get("/api/screenshot/{screenshot_id}")
    @validate_request()
    def get_screenshot(screenshot_id: str):
        dev_mode = os.getenv("RUN_MODE") != "production"
        if dev_mode:
            path = f"../config/images"
        else:
            path = f"/config/images"
        image_path = os.path.join(path, f"{screenshot_id}.png")

        if os.path.isfile(image_path):
            return FileResponse(image_path, media_type="image/png")
        else:
            raise NotFoundException(f"Image with id {screenshot_id} was not found")
