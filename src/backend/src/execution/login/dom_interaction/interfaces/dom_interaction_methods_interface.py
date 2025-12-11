from abc import ABC, abstractmethod


class DomInteractionMethodsInterface(ABC):
    @abstractmethod
    def fill_text(self, xpath, value):
        pass

    @abstractmethod
    def click_button(self, xpath):
        pass

    @abstractmethod
    def open_url(self, url):
        pass

    @abstractmethod
    def wait(self, ms):
        pass
