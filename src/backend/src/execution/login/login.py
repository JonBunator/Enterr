import os
import traceback
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
    FAILED = ActionStatusCode.FAILED

TIMEOUT = 30

def login(url: str, success_url: str, username: str, password: str, pin: str, x_paths: XPaths = None,
          screenshot_id: str = None) -> LoginStatusCode:
    try:
        with SB(uc=True, ad_block=True, xvfb=True) as sb:
            sb.activate_cdp_mode(url)
            sb.uc_gui_click_captcha()
            x_paths_automatic = find_login_automatically(sb.cdp.get_element_html('html'), pin=pin != '' and pin is not None)

            if x_paths_automatic is not None:
                username_xpath = x_paths_automatic.username
                password_xpath = x_paths_automatic.password
                pin_xpath = x_paths_automatic.pin
                submit_button_xpath = x_paths_automatic.submit_button

            if x_paths is None:
                if x_paths_automatic is None:
                    return LoginStatusCode.AUTOMATIC_FORM_DETECTION_FAILED
            else:
                if x_paths.username is not None:
                    username_xpath = x_paths.username
                if x_paths.password is not None:
                    password_xpath = x_paths.password
                if x_paths.pin is not None:
                    pin_xpath = x_paths.pin
                if x_paths.submit_button is not None:
                    submit_button_xpath = x_paths.submit_button

            if sb.cdp.send_keys(username_xpath, username) == False:
                return LoginStatusCode.USERNAME_FIELD_NOT_FOUND

            sb.sleep(0.5)

            if sb.cdp.send_keys(password_xpath, password) == False:
                return LoginStatusCode.PASSWORD_FIELD_NOT_FOUND

            if pin != '' and pin is not None:
                sb.sleep(0.5)
                if sb.cdp.send_keys(pin_xpath, pin) == False:
                    return LoginStatusCode.PIN_FIELD_NOT_FOUND


            sb.sleep(0.5)

            if sb.cdp.click(submit_button_xpath) == False:
                return LoginStatusCode.SUBMIT_BUTTON_NOT_FOUND

            # Wait for expected url
            for i in range(TIMEOUT):
                sb.sleep(1)
                if sb.cdp.get_current_url() == success_url:
                    break
            if screenshot_id is not None:
                save_screenshot(sb, screenshot_id)
            if sb.cdp.get_current_url() == success_url:
                return LoginStatusCode.SUCCESS
            return LoginStatusCode.FAILED
    except Exception as ex:
        traceback.print_exc()
        return LoginStatusCode.FAILED

def save_screenshot(sb: SB, screenshot_id: str):
    dev_mode = os.getenv('FLASK_ENV') != 'production'

    if dev_mode:
        path = f"../config/images"
    else:
        path = f"/config/images"
    sb.cdp.save_screenshot(os.path.join(path, f"{screenshot_id}.png"))
