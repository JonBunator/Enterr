import asyncio

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi_pagination import Page
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import StreamingResponse

from dataAccess.data_access import DataAccess
from dataAccess.database.database import get_db, db_session
from endpoints.models.action_history_model import (
    GetActionHistory,
    GetLastSuccessfulLogin,
)
from execution.live_view import FRAME_RATE, LiveView


def register_action_history_endpoints(
    app: FastAPI, data_access: DataAccess, live_view: LiveView
):
    # ---------------------------- GET ----------------------------
    @app.get(
        "/api/action_history",
        response_model=Page[GetActionHistory],
        tags=["Action History"],
    )
    def get_action_histories(
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
    def get_action_history(
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
    def get_last_successful_login(
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

    @app.get(
        "/api/action_history/{action_history_id}/live",
        tags=["Action History"],
    )
    def get_live_view(
        action_history_id: int,
        request: Request,
        current_user=Depends(DataAccess.get_current_user),
        # Close the session before streaming, the stream can stay open for minutes
        session: Session = Depends(get_db, scope="function"),
    ):
        db_session.set(session)
        # Raises a 404 if the action history does not belong to the current user
        DataAccess.get_action_history(action_history_id, current_user)

        live_session = live_view.subscribe(action_history_id)
        if live_session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No live view for ActionHistory {action_history_id}",
            )

        async def frame_stream():
            last_sequence = 0
            # Ends as soon as the login finishes, the session is never reused
            while not live_session.closed:
                if await request.is_disconnected():
                    break
                sequence, frame = live_session.get_frame()
                if frame is not None and sequence != last_sequence:
                    last_sequence = sequence
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n"
                        + f"Content-Length: {len(frame)}\r\n\r\n".encode()
                        + frame
                        + b"\r\n"
                    )
                await asyncio.sleep(1 / FRAME_RATE)

        return StreamingResponse(
            frame_stream(),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
            },
        )

    # ---------------------------- ADD ----------------------------
    @app.post(
        "/api/action_history/manual_add/{website_id}",
        response_model=GetActionHistory,
        tags=["Action History"],
    )
    def add_manual_action_history(
        website_id: int,
        current_user=Depends(DataAccess.get_current_user),
        session: Session = Depends(get_db),
    ):
        db_session.set(session)
        action_history = data_access.add_manual_action_history(website_id, current_user)
        return GetActionHistory.from_sql_model(action_history)
