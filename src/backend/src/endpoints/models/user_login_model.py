from pydantic import BaseModel

from dataAccess.database.database import User
from endpoints.decorators.get_request_validator import GetRequestBaseModel


class UserLogin(BaseModel):
    username: str
    password: str


class GetUserData(GetRequestBaseModel):
    username: str
    logged_in: bool

    @staticmethod
    def from_sql_model(user: User) -> "GetUserData":
        if user is None or user.is_anonymous:
            username = ''
        else:
            username = user.username
        is_logged_in = user is not None and user.is_authenticated
        return GetUserData(username=username, logged_in=is_logged_in)
