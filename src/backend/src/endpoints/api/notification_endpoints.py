from fastapi import FastAPI, Depends, HTTPException
from fastapi_pagination import Page
from starlette import status
from dataAccess.data_access import DataAccess
from endpoints.models.notification_model import (
    AddNotification,
    GetNotification,
    EditNotification,
)
from execution.notifications.notification_manager import NotificationManager


def register_notification_endpoints(
    app: FastAPI, data_access: DataAccess, notification_manager: NotificationManager
):
    # ---------------------------- GET ----------------------------
    @app.get("/api/notifications", response_model=Page[GetNotification], tags=["Notifications"])
    def get_notifications(
        current_user=Depends(DataAccess.get_current_user),
    ):
        return DataAccess.get_notifications(current_user)

    # ---------------------------- ADD ----------------------------
    @app.post("/api/notifications", response_model=GetNotification, tags=["Notifications"])
    def add_notification(
        notification_request: AddNotification,
        current_user=Depends(DataAccess.get_current_user),
    ):
        notification = data_access.add_notification(notification_request, current_user)
        return GetNotification.from_sql_model(notification)

    # ---------------------------- EDIT ----------------------------
    @app.put("/api/notifications/{notification_id}", tags=["Notifications"])
    def edit_notification(
            notification_id: int,
            notification_request: EditNotification,
            current_user=Depends(DataAccess.get_current_user),
    ):
        data_access.edit_notification(notification_id, notification_request, current_user)

    # ---------------------------- DELETE ----------------------------
    @app.delete("/api/notifications/{notification_id}", tags=["Notifications"])
    def delete_notification(
        notification_id: int,
        current_user=Depends(DataAccess.get_current_user),
    ):
        data_access.delete_notification(notification_id, current_user)

    # ---------------------------- OTHER ----------------------------
    @app.post("/api/notifications/test", tags=["Notifications"])
    def test_notification(
        notification_request: AddNotification,
        current_user=Depends(DataAccess.get_current_user),
    ):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        notification_manager.test_notification(notification_request.to_sql_model())




