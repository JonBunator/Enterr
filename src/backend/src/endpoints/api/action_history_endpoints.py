from fastapi import FastAPI, Depends
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from dataAccess.data_access import DataAccess
from dataAccess.database.database import get_db, db_session
from endpoints.models.action_history_model import (
    GetActionHistory,
    GetLastSuccessfulLogin,
)


def register_action_history_endpoints(app: FastAPI, data_access: DataAccess):
    # ---------------------------- GET ----------------------------
    @app.get(
        "/api/action_history",
        response_model=Page[GetActionHistory],
        tags=["Action History"],
    )
    async def get_action_histories(
        website_id: int,
        current_user=Depends(DataAccess.get_current_user),
        session: Session = Depends(get_db),
    ):
        db_session.set(session)
        return DataAccess.get_action_histories(website_id, current_user)

    @app.get(
        "/api/action_history/{action_history_id}",
        response_model=GetActionHistory,
        tags=["Action History"],
    )
    async def get_action_history(
        action_history_id: int,
        current_user=Depends(DataAccess.get_current_user),
        session: Session = Depends(get_db),
    ):
        db_session.set(session)
        action_history = DataAccess.get_action_history(action_history_id, current_user)
        return GetActionHistory.from_sql_model(action_history)

    @app.get(
        "/api/action_history/last_successful_login/{website_id}",
        response_model=GetLastSuccessfulLogin,
        tags=["Action History"],
    )
    async def get_last_successful_login(
        website_id: int,
        current_user=Depends(DataAccess.get_current_user),
        session: Session = Depends(get_db),
    ):
        db_session.set(session)
        action_history = DataAccess.get_last_successful_login(website_id, current_user)
        action_history_result = None
        if action_history is not None:
            action_history_result = GetActionHistory.from_sql_model(action_history)

        return GetLastSuccessfulLogin(action_history=action_history_result)

    # ---------------------------- ADD ----------------------------
    @app.post(
        "/api/action_history/manual_add/{website_id}",
        response_model=GetActionHistory,
        tags=["Action History"],
    )
    async def add_manual_action_history(
        website_id: int,
        current_user=Depends(DataAccess.get_current_user),
        session: Session = Depends(get_db),
    ):
        db_session.set(session)
        action_history = data_access.add_manual_action_history(website_id, current_user)
        return GetActionHistory.from_sql_model(action_history)
