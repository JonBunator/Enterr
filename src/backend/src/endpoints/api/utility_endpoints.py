import os
import uuid
from fastapi import FastAPI, Depends, HTTPException
from starlette import status
from starlette.responses import FileResponse
from sqlalchemy.orm import Session

from dataAccess.data_access import DataAccess
from dataAccess.database.database import get_db, db_session


def register_utility_endpoints(app: FastAPI):
    @app.get("/api/screenshot/{screenshot_id}", tags=["Other"])
    def get_screenshot(
        screenshot_id: str,
        current_user=Depends(DataAccess.get_current_user),
        session: Session = Depends(get_db),
    ):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        not_found = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with id {screenshot_id} was not found",
        )
        try:
            # Screenshot ids are always UUIDs, this also rules out path tricks
            uuid.UUID(screenshot_id)
        except ValueError:
            raise not_found
        db_session.set(session)
        # Raises a 404 if the screenshot does not belong to the current user
        DataAccess.get_action_history_by_screenshot(screenshot_id, current_user)

        dev_mode = os.getenv("RUN_MODE") != "production"
        if dev_mode:
            path = f"../config/images"
        else:
            path = f"/config/images"
        image_path = os.path.join(path, f"{screenshot_id}.png")

        if os.path.isfile(image_path):
            return FileResponse(image_path, media_type="image/png")
        else:
            raise not_found

    @app.get("/api/health", tags=["Other"])
    async def health_check():
        return {"status": "healthy"}

    @app.post("/api/trigger_login/{website_id}", tags=["Other"])
    def trigger_login(
        website_id: int,
        current_user=Depends(DataAccess.get_current_user),
        session: Session = Depends(get_db),
    ):
        db_session.set(session)
        DataAccess.trigger_login(website_id, current_user)
