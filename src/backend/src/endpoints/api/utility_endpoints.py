import os
from fastapi import FastAPI, Depends, HTTPException
from starlette import status
from starlette.responses import FileResponse
from dataAccess.data_access import DataAccess


def register_utility_endpoints(app: FastAPI):
    @app.get("/api/screenshot/{screenshot_id}", tags=["Other"])
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image with id {screenshot_id} was not found",
            )

    @app.get("/api/health", tags=["Other"])
    def health_check():
        return {"status": "healthy"}

    @app.post("/api/trigger_login/{website_id}", tags=["Other"])
    def trigger_login(
            website_id: int,
            current_user=Depends(DataAccess.get_current_user),
    ):
        DataAccess.trigger_login(website_id, current_user)
