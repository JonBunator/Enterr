from abc import ABC, abstractmethod


class DomInteractionDriverInterface(ABC):
    @abstractmethod
    def save_screenshot(self, screenshot_id: str):
        pass

    @abstractmethod
    def is_element_visible(self, xpath: str) -> bool:
        pass

    @abstractmethod
    def find_element(self, xpath: str) -> bool:
        pass

    @abstractmethod
    def solve_captcha(self):
        pass

    @abstractmethod
    def disconnect_driver(self):
        pass

    @abstractmethod
    def get_page_html(self) -> str:
        pass

    @abstractmethod
    def get_current_url(self) -> str:
        pass
