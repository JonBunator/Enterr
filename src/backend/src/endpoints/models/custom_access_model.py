from typing import Optional
from pydantic import BaseModel
from database.database import CustomAccess
from endpoints.decorators.get_request_validator import GetRequestBaseModel


class AddCustomAccess(BaseModel):
    username_xpath: str
    password_xpath: str
    pin_xpath: Optional[str] = None
    submit_button_xpath: str


class GetCustomAccess(GetRequestBaseModel):
    id: int
    username_xpath: str
    password_xpath: str
    pin_xpath: Optional[str] = None
    submit_button_xpath: str

    @staticmethod
    def from_sql_model(custom_access: CustomAccess) -> "AddCustomAccess":
        return GetCustomAccess(
            id=custom_access.id,
            username_xpath=custom_access.username_xpath,
            password_xpath=custom_access.password_xpath,
            pin_xpath=custom_access.pin_xpath,
            submit_button_xpath=custom_access.submit_button_xpath,
        )