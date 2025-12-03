from execution.login.constants import LoginStatusCode
from execution.login.custom_login.custom_login_methods_interfaces import CustomLoginMethods
from seleniumbase import SB

from execution.login.find_form_automatically import XPaths
from utils.exceptions import ScriptExecutionStopped


class CustomLoginMethodsSeleniumbase(CustomLoginMethods):
    def __init__(self, driver: SB, x_paths: XPaths, username: str, password: str):
        self._driver = driver
        self._x_paths = x_paths
        self._username = username
        self._password = password

    def click_submit_button(self, xpath=None):
        if xpath is None:
            xpath = self._x_paths.submit_button if self._x_paths is not None else None
            if xpath is None:
                raise ScriptExecutionStopped(LoginStatusCode.SUBMIT_BUTTON_NOT_FOUND, None)
        try:
            self._driver.cdp.click(xpath)
        except Exception:
            raise ScriptExecutionStopped(LoginStatusCode.SUBMIT_BUTTON_NOT_FOUND, f"XPath \"{xpath}\" not found on page.")
        self._driver.sleep(0.5)

    def fill_username(self, xpath=None):
        if xpath is None:
            xpath = self._x_paths.username if self._x_paths is not None else None
            if xpath is None:
                raise ScriptExecutionStopped(LoginStatusCode.USERNAME_FIELD_NOT_FOUND, None)
        try:
            self._driver.cdp.send_keys(xpath, self._username)
        except Exception:
            raise ScriptExecutionStopped(LoginStatusCode.USERNAME_FIELD_NOT_FOUND, f"XPath \"{xpath}\" not found on page.")
        self._driver.sleep(0.5)

    def fill_password(self, xpath=None):
        if xpath is None:
            xpath = self._x_paths.password if self._x_paths is not None else None
            if xpath is None:
                raise ScriptExecutionStopped(LoginStatusCode.PASSWORD_FIELD_NOT_FOUND, None)
        try:
            self._driver.cdp.send_keys(xpath, self._password)
        except Exception:
            raise ScriptExecutionStopped(LoginStatusCode.PASSWORD_FIELD_NOT_FOUND, f"XPath \"{xpath}\" not found on page.")
        self._driver.sleep(0.5)

    def fill_text(self, xpath, value):
        try:
            self._driver.cdp.send_keys(xpath, value)
        except Exception:
            raise ScriptExecutionStopped(LoginStatusCode.TEXT_FIELD_NOT_FOUND, f"XPath \"{xpath}\" not found on page.")
        self._driver.sleep(0.5)

    def click_button(self, xpath):
        try:
            self._driver.cdp.click(xpath)
        except Exception:
            raise ScriptExecutionStopped(LoginStatusCode.BUTTON_NOT_FOUND, f"XPath \"{xpath}\" not found on page.")
        self._driver.sleep(0.5)

    def open_url(self, url):
        self._driver.cdp.open(url)

    def wait(self, ms):
        self._driver.sleep(ms / 1000)
