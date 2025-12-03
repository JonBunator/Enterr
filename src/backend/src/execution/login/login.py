import os
import traceback
from typing import Tuple
from seleniumbase import SB
from utils.utils import compare_urls
from .constants import LoginStatusCode, CustomFailedDetailsMessage, TIMEOUT
from .custom_login.custom_login_methods_implementation import CustomLoginMethodsSeleniumbase
from .custom_login.parser import CustomLoginScriptParser
from .find_form_automatically import find_login_automatically, XPaths
from .selenium_adapter import SeleniumbaseDriver


def login(
    url: str,
    success_url: str,
    username: str,
    password: str,
    custom_login_script: str | None = None,
    screenshot_id: str | None = None,
) -> Tuple[LoginStatusCode, CustomFailedDetailsMessage]:

    try:
        with SB(uc=True, headed=True, window_size="1920,953") as sb:
            try:
                sb.activate_cdp_mode(url)
                sb.uc_gui_handle_captcha()

                if custom_login_script is None:
                    status = standard_login(sb, username, password)
                else:
                    status = custom_login(sb, custom_login_script, username, password)

                if status is not None:
                    save_screenshot(sb, screenshot_id)
                    return status

                # Redirect to success url
                sb.cdp.open(success_url)

                # Wait for expected url
                for i in range(TIMEOUT):
                    sb.uc_gui_click_captcha()
                    sb.sleep(1)
                    if compare_urls(sb.cdp.get_current_url(), success_url):
                        save_screenshot(sb, screenshot_id)
                        return LoginStatusCode.SUCCESS, None
                save_screenshot(sb, screenshot_id)

            except Exception as ex:
                traceback.print_exc()
                save_screenshot(sb, screenshot_id)
                sb.reconnect()
                sb.driver.quit()
                return LoginStatusCode.UNKNOWN_EXECUTION_ERROR, None

            current_url = sb.cdp.get_current_url()
            success_url_not_matching_custom_failed_details_message = (
                f'Expected: "{success_url}", Found: "{current_url}"'
            )
            return (
                LoginStatusCode.SUCCESS_URL_DID_NOT_MATCH,
                success_url_not_matching_custom_failed_details_message,
            )
    except Exception as ex:
        traceback.print_exc()
        sb.reconnect()
        sb.driver.quit()
        return LoginStatusCode.UNKNOWN_EXECUTION_ERROR, None


def standard_login(sb: SB, username: str, password: str) -> Tuple[LoginStatusCode, CustomFailedDetailsMessage] | None:
    xpaths = None
    # Wait until paths are found
    for i in range(0, TIMEOUT, 5):
        sb.uc_gui_click_captcha()
        xpaths, error = _find_elements(sb=sb)
        if xpaths is not None:
            break
        sb.sleep(5)
    if xpaths is None:
        return error, None

    username_xpath = xpaths.username
    password_xpath = xpaths.password
    submit_button_xpath = xpaths.submit_button

    if sb.cdp.send_keys(username_xpath, username) == False:
        return LoginStatusCode.USERNAME_FIELD_NOT_FOUND, None

    sb.sleep(0.5)

    if sb.cdp.send_keys(password_xpath, password) == False:
        return LoginStatusCode.PASSWORD_FIELD_NOT_FOUND, None

    sb.sleep(0.5)

    if sb.cdp.click(submit_button_xpath) == False:
        return LoginStatusCode.SUBMIT_BUTTON_NOT_FOUND, None

    return None


def custom_login(sb: SB, custom_login_script, username: str, password: str) -> Tuple[LoginStatusCode, CustomFailedDetailsMessage] | None:
    xpaths, error = _find_elements(sb=sb)
    custom_login_seleniumbase = CustomLoginMethodsSeleniumbase(driver=sb, x_paths=xpaths, username=username, password=password)
    parser = CustomLoginScriptParser(custom_login_seleniumbase)
    exception = parser.execute(custom_login_script)
    if exception is not None:
        return exception.status, exception.message
    return None


def _find_elements(sb: SB) -> tuple[XPaths | None, LoginStatusCode | None]:
    selenium_driver = SeleniumbaseDriver(sb)
    x_paths_automatic = find_login_automatically(
        selenium_driver, sb.cdp.get_element_html("html"),
    )
    username_xpath = None
    password_xpath = None
    submit_button_xpath = None

    if x_paths_automatic is not None:
        username_xpath = x_paths_automatic.username
        password_xpath = x_paths_automatic.password
        submit_button_xpath = x_paths_automatic.submit_button

    if x_paths_automatic is None:
        return None, LoginStatusCode.AUTOMATIC_FORM_DETECTION_FAILED

    if username_xpath is None or sb.cdp.find_element(username_xpath) is None:
        return None, LoginStatusCode.USERNAME_FIELD_NOT_FOUND
    if password_xpath is None or sb.cdp.find_element(password_xpath) is None:
        return None, LoginStatusCode.PASSWORD_FIELD_NOT_FOUND
    if submit_button_xpath is None or sb.cdp.find_element(submit_button_xpath) is None:
        return None, LoginStatusCode.SUBMIT_BUTTON_NOT_FOUND

    return XPaths(username_xpath, password_xpath, submit_button_xpath), None


def save_screenshot(sb: SB, screenshot_id: str):
    if screenshot_id is None:
        return
    dev_mode = os.getenv("RUN_MODE") != "production"

    if dev_mode:
        path = f"../config/images"
    else:
        path = f"/config/images"
    sb.cdp.save_screenshot(os.path.join(path, f"{screenshot_id}.png"), selector="body")
