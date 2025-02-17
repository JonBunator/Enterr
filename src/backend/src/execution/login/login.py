import os
import traceback
from collections import namedtuple
from enum import Enum
from seleniumbase import SB
from dataAccess.database.database import ActionFailedDetails, ActionStatusCode
from .find_form_automatically import find_login_automatically, XPaths


class LoginStatusCode(Enum):
    SUCCESS = ActionStatusCode.SUCCESS
    AUTOMATIC_FORM_DETECTION_FAILED = ActionFailedDetails.AUTOMATIC_FORM_DETECTION_FAILED
    USERNAME_FIELD_NOT_FOUND = ActionFailedDetails.USERNAME_FIELD_NOT_FOUND
    PASSWORD_FIELD_NOT_FOUND = ActionFailedDetails.PASSWORD_FIELD_NOT_FOUND
    PIN_FIELD_NOT_FOUND = ActionFailedDetails.PIN_FIELD_NOT_FOUND
    SUBMIT_BUTTON_NOT_FOUND = ActionFailedDetails.SUBMIT_BUTTON_NOT_FOUND
    SUCCESS_URL_DID_NOT_MATCH = ActionFailedDetails.SUCCESS_URL_DID_NOT_MATCH
    UNKNOWN_EXECUTION_ERROR = ActionFailedDetails.UNKNOWN_EXECUTION_ERROR
    FAILED = ActionStatusCode.FAILED

TIMEOUT = 30


def login(url: str, success_url: str, username: str, password: str, pin: str, x_paths: XPaths = None,
          screenshot_id: str = None) -> LoginStatusCode:
    try:
        with SB(uc=True, ad_block=True, xvfb=True) as sb:
            sb.activate_cdp_mode(url)
            sb.uc_gui_click_captcha()

            # Wait until paths are found
            for i in range(0, TIMEOUT, 5):
                elements, error = find_elements(sb=sb, x_paths=x_paths, pin=pin)
                if elements is not None:
                    break
                sb.sleep(5)
            if elements is None:
                save_screenshot(sb, screenshot_id)
                return error

            username_xpath = elements.username
            password_xpath = elements.password
            pin_xpath = elements.pin
            submit_button_xpath = elements.submit_button


            if sb.cdp.send_keys(username_xpath, username) == False:
                save_screenshot(sb, screenshot_id)
                return LoginStatusCode.USERNAME_FIELD_NOT_FOUND

            sb.sleep(0.5)

            if sb.cdp.send_keys(password_xpath, password) == False:
                save_screenshot(sb, screenshot_id)
                return LoginStatusCode.PASSWORD_FIELD_NOT_FOUND

            if pin != '' and pin is not None:
                sb.sleep(0.5)
                if sb.cdp.send_keys(pin_xpath, pin) == False:
                    save_screenshot(sb, screenshot_id)
                    return LoginStatusCode.PIN_FIELD_NOT_FOUND


            sb.sleep(0.5)

            if sb.cdp.click(submit_button_xpath) == False:
                save_screenshot(sb, screenshot_id)
                return LoginStatusCode.SUBMIT_BUTTON_NOT_FOUND

            # Wait for expected url
            for i in range(TIMEOUT):
                sb.sleep(1)
                if sb.cdp.get_current_url() == success_url:
                    save_screenshot(sb, screenshot_id)
                    return LoginStatusCode.SUCCESS
            save_screenshot(sb, screenshot_id)
            return LoginStatusCode.SUCCESS_URL_DID_NOT_MATCH
    except Exception as ex:
        traceback.print_exc()
        save_screenshot(sb, screenshot_id)
        return LoginStatusCode.UNKNOWN_EXECUTION_ERROR


def find_elements(sb: SB, x_paths: XPaths, pin: str) -> tuple[XPaths | None, LoginStatusCode | None] :
    pin_used = pin != '' and pin is not None
    x_paths_automatic = find_login_automatically(sb.cdp.get_element_html('html'), pin_used=pin_used)
    username_xpath = None
    password_xpath = None
    pin_xpath = None
    submit_button_xpath = None

    if x_paths_automatic is not None:
        username_xpath = x_paths_automatic.username
        password_xpath = x_paths_automatic.password
        pin_xpath = x_paths_automatic.pin
        submit_button_xpath = x_paths_automatic.submit_button

    if x_paths is None:
        if x_paths_automatic is None:
            return None, LoginStatusCode.AUTOMATIC_FORM_DETECTION_FAILED
    else:
        if x_paths.username is not None:
            username_xpath = x_paths.username
        if x_paths.password is not None:
            password_xpath = x_paths.password
        if x_paths.pin is not None:
            pin_xpath = x_paths.pin
        if x_paths.submit_button is not None:
            submit_button_xpath = x_paths.submit_button

    if username_xpath is None or sb.cdp.find_element(username_xpath) is None:
        return None, LoginStatusCode.USERNAME_FIELD_NOT_FOUND
    if password_xpath is None or sb.cdp.find_element(password_xpath) is None:
        return None, LoginStatusCode.PASSWORD_FIELD_NOT_FOUND
    if pin_used:
        if pin_xpath is not None or sb.cdp.find_element(pin_xpath) is None:
            return None, LoginStatusCode.PIN_FIELD_NOT_FOUND
    if submit_button_xpath is None or sb.cdp.find_element(submit_button_xpath) is None:
        return None, LoginStatusCode.SUBMIT_BUTTON_NOT_FOUND

    return XPaths(username_xpath, password_xpath, pin_xpath, submit_button_xpath), None


def save_screenshot(sb: SB, screenshot_id: str):
    if screenshot_id is None:
        return
    dev_mode = os.getenv('FLASK_ENV') != 'production'

    if dev_mode:
        path = f"../config/images"
    else:
        path = f"/config/images"
    sb.cdp.save_screenshot(os.path.join(path, f"{screenshot_id}.png"))
