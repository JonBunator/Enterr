from typing import Optional
from pydantic import BaseModel
from dataAccess.database.database import CustomAccess
from endpoints.decorators.get_request_validator import GetRequestBaseModel


class AddCustomAccess(BaseModel):
    username_xpath: str
    password_xpath: str
    pin_xpath: Optional[str] = None
    submit_button_xpath: str

class EditCustomAccess(BaseModel):
    id: int
    username_xpath: Optional[str] = None
    password_xpath: Optional[str] = None
    pin_xpath: Optional[str] = None
    submit_button_xpath: Optional[str] = None

    def edit_existing_model(self, existing_custom_access: CustomAccess) -> CustomAccess:
        if self.username_xpath is not None:
            existing_custom_access.username_xpath = self.username_xpath
        if self.password_xpath is not None:
            existing_custom_access.password_xpath = self.password_xpath
        if self.pin_xpath is not None:
            existing_custom_access.pin_xpath = self.pin_xpath
        if self.submit_button_xpath is not None:
            existing_custom_access.submit_button_xpath = self.submit_button_xpath
        return existing_custom_access

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