from abc import ABC, abstractmethod


class DomInteractionMethodsInterface(ABC):
    @abstractmethod
    async def fill_text(self, xpath: str, value: str):
        pass

    @abstractmethod
    async def click_button(self, xpath: str):
        pass

    @abstractmethod
    async def open_url(self, url: str):
        pass

    @abstractmethod
    async def wait(self, ms: int):
        """
        Pauses the execution for specified time.
        :param ms: Time to wait in milliseconds.
        """
        pass
