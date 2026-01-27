from typing import List
from fastapi import FastAPI, Depends
from dataAccess.data_access import DataAccess
from dataAccess.database.change_database import DataBase
from endpoints.models.action_history_model import (
    GetActionHistory,
)


def register_action_history_endpoints(app: FastAPI, data_access: DataAccess):
    # ---------------------------- GET ----------------------------
    @app.get("/api/action_history", response_model=List[GetActionHistory])
    def get_action_histories(
            website_id: int, current_user=Depends(DataAccess.get_current_user)
    ):
        action_histories = DataBase.get_action_histories(website_id, current_user)
        return [GetActionHistory.from_sql_model(d) for d in action_histories]

    @app.get("/api/action_history/{action_history_id}", response_model=GetActionHistory)
    def get_action_history(
            action_history_id: int, current_user=Depends(DataAccess.get_current_user)
    ):
        action_history = DataBase.get_action_history(action_history_id, current_user)
        return GetActionHistory.from_sql_model(action_history)

    # ---------------------------- ADD ----------------------------
    @app.post("/api/action_history/manual_add/{website_id}")
    async def add_manual_action_history(
            website_id: int,
            current_user=Depends(DataAccess.get_current_user),
    ):
        data_access.add_manual_action_history(website_id, current_user)
