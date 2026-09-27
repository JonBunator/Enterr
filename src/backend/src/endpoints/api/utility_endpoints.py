import os
import asyncio
from contextlib import suppress
from fastapi import FastAPI, Depends, HTTPException
from fastapi import Request, Query
from starlette import status
from starlette.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from dataAccess.data_access import DataAccess
from dataAccess.database.database import get_db, db_session


def register_utility_endpoints(app: FastAPI):
    @app.get("/api/screenshot/{screenshot_id}", tags=["Other"])
    def get_screenshot(
        screenshot_id: str,
        current_user=Depends(DataAccess.get_current_user),
    ):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        dev_mode = os.getenv("RUN_MODE") != "production"
        if dev_mode:
            path = "../config/images"
        else:
            path = "/config/images"
        image_path = os.path.join(path, f"{screenshot_id}.png")

        if os.path.isfile(image_path):
            return FileResponse(image_path, media_type="image/png")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image with id {screenshot_id} was not found",
            )

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

    @app.get("/api/stream/display", tags=["Other"])
    async def stream_display(
        request: Request,
        current_user=Depends(DataAccess.get_current_user),
        display: str = Query(default=os.getenv("DISPLAY", ":99")),
        fps: int = Query(default=12, ge=1, le=60),
        quality: int = Query(default=5, ge=2, le=31),
    ):
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        ffmpeg_command = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-fflags",
            "nobuffer",
            "-f",
            "x11grab",
            "-draw_mouse",
            "1",
            "-framerate",
            str(fps),
            "-i",
            display,
            "-an",
            "-c:v",
            "mjpeg",
            "-q:v",
            str(quality),
            "-f",
            "mjpeg",
            "pipe:1",
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *ffmpeg_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ffmpeg is not installed on this server",
            ) from exc

        async def frame_stream():
            jpeg_start = b"\xff\xd8"
            jpeg_end = b"\xff\xd9"
            buffer = b""

            try:
                while True:
                    if await request.is_disconnected():
                        break

                    chunk = await process.stdout.read(8192)
                    if not chunk:
                        break
                    buffer += chunk

                    while True:
                        start = buffer.find(jpeg_start)
                        if start == -1:
                            break
                        end = buffer.find(jpeg_end, start + 2)
                        if end == -1:
                            break

                        frame = buffer[start : end + 2]
                        buffer = buffer[end + 2 :]
                        yield (
                            b"--frame\r\n"
                            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                        )
            finally:
                if process.returncode is None:
                    process.terminate()
                    with suppress(asyncio.TimeoutError):
                        await asyncio.wait_for(process.wait(), timeout=2)
                if process.returncode is None:
                    process.kill()
                    with suppress(asyncio.TimeoutError):
                        await asyncio.wait_for(process.wait(), timeout=2)

        return StreamingResponse(
            frame_stream(),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={"Cache-Control": "no-store"},
        )
