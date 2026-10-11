import asyncio

from fastapi import FastAPI, Depends, HTTPException
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
from execution.login_live_view import LoginLiveView


def register_action_history_endpoints(
    app: FastAPI, data_access: DataAccess, login_live_view: LoginLiveView
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
    def get_login_live_view(
        action_history_id: int,
        current_user=Depends(DataAccess.get_current_user),
        # Close the session before streaming, the stream can stay open for minutes
        session: Session = Depends(get_db, scope="function"),
    ):
        db_session.set(session)
        # Raises a 404 if the action history does not belong to the current user
        DataAccess.get_action_history(action_history_id, current_user)

        live_session = login_live_view.subscribe(action_history_id)
        if live_session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No live view for ActionHistory {action_history_id}",
            )

        async def frame_stream():
            loop = asyncio.get_running_loop()
            changed = asyncio.Event()

            def on_change():
                # Called from the capture thread
                try:
                    loop.call_soon_threadsafe(changed.set)
                except RuntimeError:
                    # The event loop is already closed
                    pass

            live_session.add_listener(on_change)
            # If the stream never starts, the viewer is released when the login ends
            try:
                last_sequence = 0
                while True:
                    changed.clear()
                    sequence, frame = live_session.get_frame()
                    # Ends as soon as the login finishes, the session is never reused
                    if live_session.closed:
                        break
                    if frame is not None and sequence != last_sequence:
                        last_sequence = sequence
                        yield (
                            b"--frame\r\n"
                            b"Content-Type: image/jpeg\r\n"
                            + f"Content-Length: {len(frame)}\r\n\r\n".encode()
                            + frame
                            + b"\r\n"
                        )
                    await changed.wait()
            finally:
                live_session.remove_listener(on_change)
                login_live_view.unsubscribe(live_session)

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
