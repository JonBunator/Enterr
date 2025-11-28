from pydantic import BaseModel

from dataAccess.database.database import User
from endpoints.decorators.request_validator import GetRequestBaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class GetUserData(GetRequestBaseModel):
    username: str

    @staticmethod
    def from_sql_model(user: User) -> "GetUserData":
        if user is None:
            username = ''
        else:
            username = user.username
        return GetUserData(username=username)
