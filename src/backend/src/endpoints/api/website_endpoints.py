from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, Query
from fastapi_filters import SortingValues, create_sorting
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from dataAccess.data_access import DataAccess
from dataAccess.database.database import get_db, db_session
from endpoints.models.website_model import (
    GetWebsite,
    AddWebsite,
    EditWebsite,
    CheckCustomLoginScript,
    CheckCustomLoginScriptResponse,
)


def register_website_endpoints(app: FastAPI, data_access: DataAccess):
    # ---------------------------- GET ----------------------------
    @app.get("/api/websites", response_model=Page[GetWebsite], tags=["Websites"])
    def get_websites(
        search: Optional[str] = Query(None),
        sorting: SortingValues = Depends(
            create_sorting("name", "next_schedule", "last_login_attempt", "status")
        ),
        session: Session = Depends(get_db),
        current_user=Depends(DataAccess.get_current_user),
    ):
        db_session.set(session)
        return DataAccess.get_websites(current_user, search, sorting)

    @app.get("/api/websites/{website_id}", response_model=GetWebsite, tags=["Websites"])
    def get_website(
        website_id: int,
        current_user=Depends(DataAccess.get_current_user),
        session: Session = Depends(get_db),
    ):
        db_session.set(session)
        website = DataAccess.get_website(website_id, current_user)
        return GetWebsite.from_sql_model(website)

    # ---------------------------- ADD ----------------------------
    @app.post("/api/websites", response_model=GetWebsite, tags=["Websites"])
    def add_website(
        website_request: AddWebsite,
        current_user=Depends(DataAccess.get_current_user),
        session: Session = Depends(get_db),
    ):
        db_session.set(session)
        return data_access.add_website(website_request, current_user)

    # ---------------------------- EDIT ----------------------------
    @app.put("/api/websites/{website_id}", tags=["Websites"])
    def edit_website(
        website_id: int,
        website_request: EditWebsite,
        current_user=Depends(DataAccess.get_current_user),
        session: Session = Depends(get_db),
    ):
        db_session.set(session)
        data_access.edit_website(website_id, website_request, current_user)

    # ---------------------------- DELETE ----------------------------
    @app.delete("/api/websites/{website_id}", tags=["Websites"])
    def delete_website(
        website_id: int,
        current_user=Depends(DataAccess.get_current_user),
        session: Session = Depends(get_db),
    ):
        db_session.set(session)
        data_access.delete_website(website_id, current_user)

    # ---------------------------- OTHER ----------------------------
    @app.post(
        "/api/websites/check_custom_login_script",
        response_model=CheckCustomLoginScriptResponse,
        tags=["Websites"],
    )
    async def check_custom_login_script(
        check_custom_login_script_request: CheckCustomLoginScript,
    ):
        return DataAccess.check_custom_login_script(check_custom_login_script_request)
