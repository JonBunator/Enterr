import os
from enum import Enum
from seleniumbase import SB
import uuid
from database.database import ActionFailedDetails, ActionStatusCode
from .find_form_automatically import find_login_automatically, XPaths

class LoginStatusCode(Enum):
    SUCCESS = ActionStatusCode.SUCCESS
    AUTOMATIC_FORM_DETECTION_FAILED = ActionFailedDetails.AUTOMATIC_FORM_DETECTION_FAILED
    USERNAME_FIELD_NOT_FOUND = ActionFailedDetails.USERNAME_FIELD_NOT_FOUND
    PASSWORD_FIELD_NOT_FOUND = ActionFailedDetails.PASSWORD_FIELD_NOT_FOUND
    PIN_FIELD_NOT_FOUND = ActionFailedDetails.PIN_FIELD_NOT_FOUND
    SUBMIT_BUTTON_NOT_FOUND = ActionFailedDetails.SUBMIT_BUTTON_NOT_FOUND
    FAILED = ActionStatusCode.FAILED

def login(url: str, success_url: str, username: str, password: str, x_paths: XPaths = None) -> LoginStatusCode:
    with SB(uc=True, ad_block=True, xvfb=True) as sb:
        sb.activate_cdp_mode(url)
        sb.sleep(3)
        sb.uc_gui_click_captcha()
        if x_paths is None:
            x_paths = find_login_automatically(sb.cdp.get_element_html('html'))
            if x_paths is None:
                return LoginStatusCode.AUTOMATIC_FORM_DETECTION_FAILED

        if sb.cdp.send_keys(x_paths.username, username) == False:
            return LoginStatusCode.USERNAME_FIELD_NOT_FOUND

        sb.sleep(0.5)

        if sb.cdp.send_keys(x_paths.password, password) == False:
            return LoginStatusCode.PASSWORD_FIELD_NOT_FOUND

        sb.sleep(0.5)

        if sb.cdp.click(x_paths.submit_button) == False:
            return LoginStatusCode.SUBMIT_BUTTON_NOT_FOUND

        sb.sleep(0.5)

        save_screenshot(sb)
        if sb.cdp.get_current_url() == success_url:
            return LoginStatusCode.SUCCESS
        return LoginStatusCode.FAILED


def save_screenshot(sb: SB) -> str:
    dev_mode = os.getenv('FLASK_ENV') != 'production'
    unique_id = str(uuid.uuid4())

    if dev_mode:
        path = f"../config/images"
    else:
        path = f"/config/images"
    sb.cdp.save_screenshot(os.path.join(path, f"{unique_id}.png"))
    return unique_id

            
