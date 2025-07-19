import os
from typing import List, Annotated
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.responses import FileResponse
from dataAccess.data_access import DataAccess
from dataAccess.database.change_database import DataBase
from endpoints.decorators.request_validator import validate_request
from endpoints.models.action_history_model import (
    AddManualActionHistory,
    GetActionHistory,
)
from endpoints.models.notification_model import (
    AddNotification,
    GetNotification,
    DeleteNotification,
    EditNotification,
)
from endpoints.models.other_model import TriggerAutomaticLogin
from endpoints.models.user_login_model import UserLogin, GetUserData, Token
from endpoints.models.website_model import (
    GetWebsite,
    AddWebsite,
    EditWebsite,
    DeleteWebsite,
)
from endpoints.webhooks.webhook_endpoints import WebhookEndpoints
from execution.notifications.notification_manager import NotificationManager
from utils.exceptions import NotFoundException, RequestValidationError
from jose import jwt
from datetime import datetime, timedelta


SECRET_KEY = "your_secret_key"  # Must match main.py
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def register_rest_endpoints(
    app: FastAPI, data_access: DataAccess, notification_manager: NotificationManager
):
    @app.get("/api/websites", response_model=List[GetWebsite])
    def get_websites(current_user=Depends(DataBase.get_current_user)):
        websites = DataBase.get_websites(current_user)
        return [GetWebsite.from_sql_model(d) for d in websites]

    @app.get("/api/websites/{website_id}", response_model=GetWebsite)
    def get_website(website_id: int, current_user=Depends(DataBase.get_current_user)):
        website = DataBase.get_website(website_id)
        return GetWebsite.from_sql_model(website)

    @app.post("/api/websites/add")
    async def add_website(
        website_request: AddWebsite, current_user=Depends(DataBase.get_current_user)
    ):
        data_access.add_website(website_request)

    @app.post("/api/websites/edit")
    async def edit_website(
        website_request: EditWebsite, current_user=Depends(DataBase.get_current_user)
    ):
        data_access.edit_website(website_request)

    @app.post("/api/websites/delete")
    async def delete_website(
        website_request: DeleteWebsite, current_user=Depends(DataBase.get_current_user)
    ):
        data_access.delete_website(website_request)

    @app.get("/api/action_history/{website_id}", response_model=List[GetActionHistory])
    def get_action_history(
        website_id: int, current_user=Depends(DataBase.get_current_user)
    ):
        action_histories = DataBase.get_action_history(website_id)
        return [GetActionHistory.from_sql_model(d) for d in action_histories]

    @app.post("/api/action_history/manual_add")
    async def add_manual_action_history(
        action_history_request: AddManualActionHistory,
        current_user=Depends(DataBase.get_current_user),
    ):
        data_access.add_manual_action_history(action_history_request)

    @app.post("/api/trigger_login")
    def trigger_login(
        login_request: TriggerAutomaticLogin,
        current_user=Depends(DataBase.get_current_user),
    ):
        DataBase.trigger_login(login_request.id)

    @app.post("/api/notifications/add")
    async def add_notification(
        notification_request: AddNotification,
        current_user=Depends(DataBase.get_current_user),
    ):
        data_access.add_notification(notification_request)

    @app.post("/api/notifications/test")
    def test_notification(
        notification_request: AddNotification,
        current_user=Depends(DataBase.get_current_user),
    ):
        notification_manager.test_notification(notification_request.to_sql_model())

    @app.post("/api/notifications/edit")
    async def edit_notification(
        notification_request: EditNotification,
        current_user=Depends(DataBase.get_current_user),
    ):
        data_access.edit_notification(notification_request)

    @app.post("/api/notifications/delete")
    async def delete_notification(
        notification_request: DeleteNotification,
        current_user=Depends(DataBase.get_current_user),
    ):
        data_access.delete_notification(notification_request)

    @app.get("/api/notifications", response_model=List[GetNotification])
    def get_notifications(current_user=Depends(DataBase.get_current_user)):
        notifications = DataBase.get_notifications()
        return [GetNotification.from_sql_model(d) for d in notifications]

    @app.post("/api/token")
    def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
        user = data_access.get_user(form_data.username)
        if user and user.check_password(form_data.password):
            access_token = create_access_token(data={"sub": user.username})
            return Token(access_token=access_token, token_type="bearer")
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    """
    @app.post("/api/user/logout")
    def logout():
        logout_user()
    """

    @app.get("/api/user/data", response_model=GetUserData)
    @validate_request()
    def get_user_data(current_user=Depends(DataBase.get_current_user)):
        user = DataBase.get_current_user()
        return GetUserData.from_sql_model(user)

    @app.get("/api/screenshot/{screenshot_id}")
    @validate_request()
    def get_screenshot(
        screenshot_id: str, current_user=Depends(DataBase.get_current_user)
    ):
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
