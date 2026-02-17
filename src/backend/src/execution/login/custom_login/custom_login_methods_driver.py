from execution.login.constants import LoginStatusCode
from execution.login.custom_login.custom_login_methods_interfaces import (
    CustomLoginMethodsInterface,
)
from execution.login.dom_interaction.interfaces.dom_interaction_interface import (
    DomInteractionInterface,
)
from execution.login.find_form_automatically import XPaths
from utils.exceptions import ScriptExecutionStopped


class CustomLoginMethodsDriver(CustomLoginMethodsInterface):
    def __init__(
        self,
        driver: DomInteractionInterface,
        x_paths: XPaths,
        username: str,
        password: str,
    ):
        self._driver = driver
        self._x_paths = x_paths
        self._username = username
        self._password = password

    async def click_submit_button(self, xpath=None):
        if xpath is None:
            xpath = self._x_paths.submit_button if self._x_paths is not None else None
            if xpath is None:
                raise ScriptExecutionStopped(
                    LoginStatusCode.SUBMIT_BUTTON_NOT_FOUND, None
                )
        try:
            await self._driver.click_button(xpath)
        except Exception:
            raise ScriptExecutionStopped(
                LoginStatusCode.SUBMIT_BUTTON_NOT_FOUND,
                f'XPath "{xpath}" not found on page.',
            )
        await self._driver.wait(500)

    async def fill_username(self, xpath=None):
        if xpath is None:
            xpath = self._x_paths.username if self._x_paths is not None else None
            if xpath is None:
                raise ScriptExecutionStopped(
                    LoginStatusCode.USERNAME_FIELD_NOT_FOUND, None
                )
        try:
            await self._driver.fill_text(xpath, self._username)
        except Exception:
            raise ScriptExecutionStopped(
                LoginStatusCode.USERNAME_FIELD_NOT_FOUND,
                f'XPath "{xpath}" not found on page.',
            )
        await self._driver.wait(500)

    async def fill_password(self, xpath=None):
        if xpath is None:
            xpath = self._x_paths.password if self._x_paths is not None else None
            if xpath is None:
                raise ScriptExecutionStopped(
                    LoginStatusCode.PASSWORD_FIELD_NOT_FOUND, None
                )
        try:
            await self._driver.fill_text(xpath, self._password)
        except Exception:
            raise ScriptExecutionStopped(
                LoginStatusCode.PASSWORD_FIELD_NOT_FOUND,
                f'XPath "{xpath}" not found on page.',
            )
        await self._driver.wait(500)

    async def fill_text(self, xpath, value):
        try:
            await self._driver.fill_text(xpath, value)
        except Exception:
            raise ScriptExecutionStopped(
                LoginStatusCode.TEXT_FIELD_NOT_FOUND,
                f'XPath "{xpath}" not found on page.',
            )
        await self._driver.wait(500)

    async def click_button(self, xpath):
        try:
            await self._driver.click_button(xpath)
        except Exception:
            raise ScriptExecutionStopped(
                LoginStatusCode.BUTTON_NOT_FOUND, f'XPath "{xpath}" not found on page.'
            )
        await self._driver.wait(500)

    async def open_url(self, url):
        await self._driver.open_url(url)

    async def wait(self, ms):
        await self._driver.wait(ms)
