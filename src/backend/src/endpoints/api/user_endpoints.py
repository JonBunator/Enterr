from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.responses import Response
from sqlalchemy.orm import Session

from dataAccess.data_access import DataAccess
from dataAccess.database.database import get_db, db_session
from endpoints.models.user_login_model import GetUserData, Token
from utils.security import create_access_token


def register_user_endpoints(app: FastAPI, data_access: DataAccess):
    @app.get("/api/user/data", response_model=GetUserData, tags=["User"])
    async def get_user_data(
        current_user=Depends(DataAccess.get_current_user),
    ):
        return GetUserData.from_sql_model(current_user)

    @app.post("/api/user/login", tags=["User"])
    def login(
        response: Response,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> Token:
        user = data_access.get_user(form_data.username)

        if user and user.check_password(form_data.password):
            access_token = create_access_token(user.username)

            response.set_cookie(
                key="access_token",
                value=f"Bearer {access_token}",
                httponly=True,
                secure=False,
                samesite="strict",
                max_age=24 * 60 * 60,
                path="/",
            )

            return Token(access_token=access_token, token_type="bearer")

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @app.post("/api/user/logout", tags=["User"])
    async def logout(response: Response):
        response.delete_cookie(
            key="access_token", path="/", httponly=True, secure=False, samesite="strict"
        )
