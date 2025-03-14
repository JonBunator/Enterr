from abc import ABC, abstractmethod
from seleniumbase import SB


class SeleniumDriver(ABC):
    @abstractmethod
    def is_element_visible(self, xpath: str) -> bool:
        pass


# Driver for the seleniumbase package
class SeleniumbaseDriver(SeleniumDriver):
    def __init__(self, sb: SB):
        self.sb = sb

    def is_element_visible(self, xpath: str) -> bool:
        return self.sb.cdp.is_element_visible(xpath)
