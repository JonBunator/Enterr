from abc import ABC, abstractmethod


class DomInteractionDriverInterface(ABC):
    @abstractmethod
    async def save_screenshot(self, screenshot_id: str):
        pass

    @abstractmethod
    async def is_element_visible(self, xpath: str) -> bool:
        pass

    @abstractmethod
    async def find_element(self, xpath: str) -> bool:
        pass

    @abstractmethod
    async def solve_captcha(self):
        pass

    @abstractmethod
    async def disconnect_driver(self):
        pass

    @abstractmethod
    async def get_page_html(self) -> str:
        pass

    @abstractmethod
    async def get_current_url(self) -> str:
        pass
