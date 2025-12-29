from abc import ABC, abstractmethod


class DomInteractionMethodsInterface(ABC):
    @abstractmethod
    def fill_text(self, xpath: str, value: str):
        pass

    @abstractmethod
    def click_button(self, xpath: str):
        pass

    @abstractmethod
    def open_url(self, url: str):
        pass

    @abstractmethod
    def wait(self, ms: int):
        """
        Pauses the execution for specified time.
        :param ms: Time to wait in milliseconds.
        """
        pass
