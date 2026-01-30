from fastapi import FastAPI, Depends, HTTPException
from fastapi_pagination import Page
from starlette import status
from sqlalchemy.orm import Session

from dataAccess.data_access import DataAccess
from dataAccess.database.database import get_db, db_session
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
    @app.get(
        "/api/notifications",
        response_model=Page[GetNotification],
        tags=["Notifications"],
    )
    async def get_notifications(
        current_user=Depends(DataAccess.get_current_user),
        session: Session = Depends(get_db),
    ):
        db_session.set(session)
        return DataAccess.get_notifications(current_user)

    # ---------------------------- ADD ----------------------------
    @app.post(
        "/api/notifications", response_model=GetNotification, tags=["Notifications"]
    )
    async def add_notification(
        notification_request: AddNotification,
        current_user=Depends(DataAccess.get_current_user),
        session: Session = Depends(get_db),
    ):
        db_session.set(session)
        notification = data_access.add_notification(notification_request, current_user)
        return GetNotification.from_sql_model(notification)

    # ---------------------------- EDIT ----------------------------
    @app.put("/api/notifications/{notification_id}", tags=["Notifications"])
    async def edit_notification(
        notification_id: int,
        notification_request: EditNotification,
        current_user=Depends(DataAccess.get_current_user),
        session: Session = Depends(get_db),
    ):
        db_session.set(session)
        data_access.edit_notification(
            notification_id, notification_request, current_user
        )

    # ---------------------------- DELETE ----------------------------
    @app.delete("/api/notifications/{notification_id}", tags=["Notifications"])
    async def delete_notification(
        notification_id: int,
        current_user=Depends(DataAccess.get_current_user),
        session: Session = Depends(get_db),
    ):
        db_session.set(session)
        data_access.delete_notification(notification_id, current_user)

    # ---------------------------- OTHER ----------------------------
    @app.post("/api/notifications/test", tags=["Notifications"])
    async def test_notification(
        notification_request: AddNotification,
        current_user=Depends(DataAccess.get_current_user),
        session: Session = Depends(get_db),
    ):
        db_session.set(session)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        notification_manager.test_notification(notification_request.to_sql_model())
