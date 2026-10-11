import pytest

from execution.login.constants import LoginStatusCode
from execution.login.find_form_automatically import XPaths
from execution.login.login import login

URL = "https://example.com/login"
SUCCESS_URL = "https://example.com/home"


@pytest.fixture(autouse=True)
def short_timeout(mocker):
    mocker.patch("execution.login.login.TIMEOUT", 2)


@pytest.fixture
def driver_cls(mocker):
    return mocker.patch("execution.login.login.DomInteractionDriver")


@pytest.fixture
def driver(driver_cls):
    driver = driver_cls.return_value.__enter__.return_value
    driver.find_element.return_value = True
    driver.get_current_url.return_value = SUCCESS_URL
    return driver


@pytest.fixture
def form_finder(mocker):
    finder = mocker.patch("execution.login.login.LoginFormFinder")
    finder.return_value.find_login_automatically.return_value = XPaths(
        "//input[@id='user']", "//input[@id='pass']", "//button"
    )
    return finder.return_value


def _login(custom_login_script=None):
    return login(
        url=URL,
        success_url=SUCCESS_URL,
        username="alice",
        password="secret",
        custom_login_script=custom_login_script,
        screenshot_id="screenshot-id",
    )


def test_login_success_with_automatic_form_detection(driver_cls, driver, form_finder):
    assert _login() == (LoginStatusCode.SUCCESS, None)

    driver_cls.assert_called_once_with(url=URL)
    driver.fill_text.assert_any_call("//input[@id='user']", "alice")
    driver.fill_text.assert_any_call("//input[@id='pass']", "secret")
    driver.click_button.assert_called_once_with("//button")
    driver.open_url.assert_called_once_with(SUCCESS_URL)
    driver.save_screenshot.assert_called_with("screenshot-id")


def test_login_username_field_not_found(driver, form_finder):
    form_finder.find_login_automatically.return_value = XPaths(
        None, "//input[@id='pass']", "//button"
    )

    assert _login() == (LoginStatusCode.USERNAME_FIELD_NOT_FOUND, None)

    driver.fill_text.assert_not_called()
    driver.save_screenshot.assert_called_once_with("screenshot-id")


def test_login_form_not_detected(driver, form_finder):
    form_finder.find_login_automatically.return_value = None

    assert _login() == (LoginStatusCode.USERNAME_FIELD_NOT_FOUND, None)


def test_login_xpath_not_present_on_page(driver, form_finder):
    driver.find_element.side_effect = lambda xpath: xpath != "//button"

    assert _login() == (LoginStatusCode.SUBMIT_BUTTON_NOT_FOUND, None)


def test_login_success_url_did_not_match(driver, form_finder):
    driver.get_current_url.return_value = URL

    assert _login() == (
        LoginStatusCode.SUCCESS_URL_DID_NOT_MATCH,
        f'Expected: "{SUCCESS_URL}", Found: "{URL}"',
    )


def test_login_driver_error_during_interaction(driver, form_finder):
    driver.open_url.side_effect = RuntimeError("browser crashed")

    assert _login() == (LoginStatusCode.UNKNOWN_EXECUTION_ERROR, None)
    driver.disconnect_driver.assert_called_once()
    driver.save_screenshot.assert_called_with("screenshot-id")


def test_login_driver_cannot_start(driver_cls):
    driver_cls.side_effect = RuntimeError("no browser")

    assert _login() == (LoginStatusCode.UNKNOWN_EXECUTION_ERROR, None)


def test_login_custom_script(driver, form_finder):
    script = """
    fillUsername()
    fillPassword()
    clickButton("//button[@id='next']")
    """

    assert _login(script) == (LoginStatusCode.SUCCESS, None)
    driver.click_button.assert_called_once_with("//button[@id='next']")


def test_login_custom_script_button_not_found(driver, form_finder):
    driver.click_button.side_effect = Exception("not found")

    assert _login('clickButton("//missing")') == (
        LoginStatusCode.BUTTON_NOT_FOUND,
        'XPath "//missing" not found on page.',
    )
    driver.open_url.assert_not_called()
