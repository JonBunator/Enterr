import os

from seleniumbase import SB
from execution.login.dom_interaction.interfaces.dom_interaction_interface import DomInteractionInterface


class DomInteractionDriver(DomInteractionInterface):

    def __enter__(self):
        self._sb_instance = SB(uc=True, headed=True, window_size="1920,953")
        self._sb = self._sb_instance.__enter__()

        self._sb.activate_cdp_mode(self._url)
        self._sb.uc_gui_handle_captcha()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._sb_instance.__exit__(exc_type, exc, tb)
        return False

    def disconnect_driver(self):
        self._sb.reconnect()
        self._sb.driver.quit()

    def get_current_url(self) -> str:
        return self._sb.cdp.get_current_url()

    def get_page_html(self) -> str:
        return self._sb.cdp.get_element_html("html")

    def is_element_visible(self, xpath: str) -> bool:
        return self._sb.cdp.is_element_visible(xpath)

    def save_screenshot(self, screenshot_id: str):
        if screenshot_id is None:
            return
        dev_mode = os.getenv("RUN_MODE") != "production"

        if dev_mode:
            path = f"../config/images"
        else:
            path = f"/config/images"
        self._sb.cdp.save_screenshot(os.path.join(path, f"{screenshot_id}.png"), selector="body")

    def find_element(self, xpath: str) -> bool:
        return self._sb.cdp.find_element(xpath) is not None

    def solve_captcha(self):
        self._sb.uc_gui_click_captcha()

    def fill_text(self, xpath: str, value: str):
        self._sb.cdp.send_keys(xpath, value)

    def click_button(self, xpath: str):
        self._sb.cdp.click(xpath)

    def open_url(self, url: str):
        self._sb.cdp.open(url)

    def wait(self, ms: int):
        self._sb.sleep(ms / 1000)

