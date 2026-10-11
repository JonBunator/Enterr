import pytest

from execution.login.constants import LoginStatusCode
from execution.login.custom_login.custom_login_methods_driver import (
    CustomLoginMethodsDriver,
)
from execution.login.find_form_automatically import XPaths
from utils.exceptions import ScriptExecutionStopped

XPATHS = XPaths("//user", "//pass", "//submit")


@pytest.fixture
def driver(mocker):
    return mocker.Mock()


def _methods(driver, x_paths=XPATHS):
    return CustomLoginMethodsDriver(
        driver=driver, x_paths=x_paths, username="alice", password="secret"
    )


def test_default_xpaths_are_used(driver):
    methods = _methods(driver)

    methods.fill_username()
    methods.fill_password()
    methods.click_submit_button()

    driver.fill_text.assert_any_call("//user", "alice")
    driver.fill_text.assert_any_call("//pass", "secret")
    driver.click_button.assert_called_once_with("//submit")


def test_explicit_xpaths_override_defaults(driver):
    methods = _methods(driver)

    methods.fill_username("//custom-user")
    methods.fill_password("//custom-pass")
    methods.click_submit_button("//custom-submit")

    driver.fill_text.assert_any_call("//custom-user", "alice")
    driver.fill_text.assert_any_call("//custom-pass", "secret")
    driver.click_button.assert_called_once_with("//custom-submit")


def test_simple_methods_forward_to_driver(driver):
    methods = _methods(driver)

    methods.fill_text("//field", "value")
    methods.click_button("//btn")
    methods.open_url("https://example.com")
    methods.wait(1000)

    driver.fill_text.assert_called_once_with("//field", "value")
    driver.click_button.assert_called_once_with("//btn")
    driver.open_url.assert_called_once_with("https://example.com")
    driver.wait.assert_any_call(1000)


@pytest.mark.parametrize(
    "method, status",
    [
        ("fill_username", LoginStatusCode.USERNAME_FIELD_NOT_FOUND),
        ("fill_password", LoginStatusCode.PASSWORD_FIELD_NOT_FOUND),
        ("click_submit_button", LoginStatusCode.SUBMIT_BUTTON_NOT_FOUND),
    ],
)
@pytest.mark.parametrize("x_paths", [None, XPaths(None, None, None)])
def test_missing_default_xpath_raises(driver, method, status, x_paths):
    with pytest.raises(ScriptExecutionStopped) as exc:
        getattr(_methods(driver, x_paths), method)()
    assert exc.value.status == status


@pytest.mark.parametrize(
    "method, args, status",
    [
        ("fill_username", (), LoginStatusCode.USERNAME_FIELD_NOT_FOUND),
        ("fill_password", (), LoginStatusCode.PASSWORD_FIELD_NOT_FOUND),
        ("click_submit_button", (), LoginStatusCode.SUBMIT_BUTTON_NOT_FOUND),
        ("fill_text", ("//field", "value"), LoginStatusCode.TEXT_FIELD_NOT_FOUND),
        ("click_button", ("//btn",), LoginStatusCode.BUTTON_NOT_FOUND),
    ],
)
def test_driver_errors_are_mapped_to_status(driver, method, args, status):
    driver.fill_text.side_effect = Exception("not found")
    driver.click_button.side_effect = Exception("not found")

    with pytest.raises(ScriptExecutionStopped) as exc:
        getattr(_methods(driver), method)(*args)
    assert exc.value.status == status
    assert "not found on page" in exc.value.message
