import os
from typing import List, Annotated
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.responses import FileResponse, Response
from dataAccess.data_access import DataAccess
from dataAccess.database.change_database import DataBase
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
from endpoints.models.user_login_model import GetUserData, Token
from endpoints.models.website_model import (
    GetWebsite,
    AddWebsite,
    EditWebsite,
    DeleteWebsite, CheckCustomLoginScript,
)
from execution.notifications.notification_manager import NotificationManager
from utils.exceptions import NotFoundException
from utils.security import create_access_token


def register_rest_endpoints(
    app: FastAPI, data_access: DataAccess, notification_manager: NotificationManager
):
    @app.get("/api/websites", response_model=List[GetWebsite])
    def get_websites(current_user=Depends(DataAccess.get_current_user)):
        websites = DataBase.get_websites(current_user)
        return [GetWebsite.from_sql_model(d) for d in websites]

    @app.get("/api/websites/{website_id}", response_model=GetWebsite)
    def get_website(website_id: int, current_user=Depends(DataAccess.get_current_user)):
        website = DataBase.get_website(website_id, current_user)
        return GetWebsite.from_sql_model(website)

    @app.post("/api/websites/add")
    async def add_website(
        website_request: AddWebsite, current_user=Depends(DataAccess.get_current_user)
    ):
        data_access.add_website(website_request, current_user)

    @app.post("/api/websites/edit")
    async def edit_website(
        website_request: EditWebsite, current_user=Depends(DataAccess.get_current_user)
    ):
        data_access.edit_website(website_request, current_user)

    @app.post("/api/websites/delete")
    async def delete_website(
        website_request: DeleteWebsite,
        current_user=Depends(DataAccess.get_current_user),
    ):
        data_access.delete_website(website_request, current_user)

    @app.post("/api/websites/check_custom_login_script")
    async def check_custom_login_script(
            check_custom_login_script_request: CheckCustomLoginScript,
    ):
        return DataAccess.check_custom_login_script(check_custom_login_script_request)

    @app.get("/api/action_history/{website_id}", response_model=List[GetActionHistory])
    def get_action_history(
        website_id: int, current_user=Depends(DataAccess.get_current_user)
    ):
        action_histories = DataBase.get_action_history(website_id, current_user)
        return [GetActionHistory.from_sql_model(d) for d in action_histories]

    @app.post("/api/action_history/manual_add")
    async def add_manual_action_history(
        action_history_request: AddManualActionHistory,
        current_user=Depends(DataAccess.get_current_user),
    ):
        data_access.add_manual_action_history(action_history_request, current_user)

    @app.post("/api/trigger_login")
    def trigger_login(
        login_request: TriggerAutomaticLogin,
        current_user=Depends(DataAccess.get_current_user),
    ):
        DataBase.trigger_login(login_request.id, current_user)

    @app.post("/api/notifications/add")
    async def add_notification(
        notification_request: AddNotification,
        current_user=Depends(DataAccess.get_current_user),
    ):
        data_access.add_notification(notification_request, current_user)

    @app.post("/api/notifications/test")
    def test_notification(
        notification_request: AddNotification,
        current_user=Depends(DataAccess.get_current_user),
    ):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        notification_manager.test_notification(notification_request.to_sql_model())

    @app.post("/api/notifications/edit")
    async def edit_notification(
        notification_request: EditNotification,
        current_user=Depends(DataAccess.get_current_user),
    ):
        data_access.edit_notification(notification_request, current_user)

    @app.post("/api/notifications/delete")
    async def delete_notification(
        notification_request: DeleteNotification,
        current_user=Depends(DataAccess.get_current_user),
    ):
        data_access.delete_notification(notification_request, current_user)

    @app.get("/api/notifications", response_model=List[GetNotification])
    def get_notifications(current_user=Depends(DataAccess.get_current_user)):
        notifications = DataBase.get_notifications(current_user)
        return [GetNotification.from_sql_model(d) for d in notifications]

    @app.post("/api/user/login")
    def login(
        response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ) -> Token:
        user = data_access.get_user(form_data.username)

        if user and user.check_password(form_data.password):
            access_token = create_access_token(user.username)

            response.set_cookie(
                key="access_token",
                value=f"Bearer {access_token}",
                httponly=True,
                secure=False,
                samesite="strict",
                max_age=24 * 60 * 60,
                path="/",
            )

            return Token(access_token=access_token, token_type="bearer")

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @app.post("/api/user/logout")
    def logout(response: Response):
        response.delete_cookie(
            key="access_token", path="/", httponly=True, secure=False, samesite="strict"
        )

    @app.get("/api/user/data", response_model=GetUserData)
    def get_user_data(current_user=Depends(DataAccess.get_current_user)):
        return GetUserData.from_sql_model(current_user)

    @app.get("/api/screenshot/{screenshot_id}")
    def get_screenshot(
        screenshot_id: str, current_user=Depends(DataAccess.get_current_user)
    ):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
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


    @app.get("/api/health")
    def health_check():
        return {"status": "healthy"}
