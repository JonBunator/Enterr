from typing import List
from fastapi import FastAPI, Depends
from dataAccess.data_access import DataAccess
from dataAccess.database.change_database import DataBase
from endpoints.models.website_model import (
    GetWebsite,
    AddWebsite,
    EditWebsite,
    CheckCustomLoginScript,
)


def register_website_endpoints(app: FastAPI, data_access: DataAccess):
    # ---------------------------- GET ----------------------------
    @app.get("/api/websites", response_model=List[GetWebsite])
    def get_websites(current_user=Depends(DataAccess.get_current_user)):
        websites = DataBase.get_websites(current_user)
        return [GetWebsite.from_sql_model(d) for d in websites]

    @app.get("/api/websites/{website_id}", response_model=GetWebsite)
    def get_website(website_id: int, current_user=Depends(DataAccess.get_current_user)):
        website = DataBase.get_website(website_id, current_user)
        return GetWebsite.from_sql_model(website)

    # ---------------------------- ADD ----------------------------
    @app.post("/api/websites")
    async def add_website(
        website_request: AddWebsite, current_user=Depends(DataAccess.get_current_user)
    ):
        data_access.add_website(website_request, current_user)

    # ---------------------------- EDIT ----------------------------
    @app.put("/api/websites/{website_id}")
    async def edit_website(
        website_id: int,
        website_request: EditWebsite,
        current_user=Depends(DataAccess.get_current_user),
    ):
        data_access.edit_website(website_id, website_request, current_user)

    # ---------------------------- DELETE ----------------------------
    @app.delete("/api/websites/{website_id}")
    async def delete_website(
        website_id: int,
        current_user=Depends(DataAccess.get_current_user),
    ):
        data_access.delete_website(website_id, current_user)

    # ---------------------------- OTHER ----------------------------
    @app.post("/api/websites/check_custom_login_script")
    async def check_custom_login_script(
        check_custom_login_script_request: CheckCustomLoginScript,
    ):
        return DataAccess.check_custom_login_script(check_custom_login_script_request)
