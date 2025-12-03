from abc import ABC, abstractmethod


class CustomLoginMethods(ABC):
    @abstractmethod
    def click_submit_button(self, xpath=None):
        pass

    @abstractmethod
    def fill_username(self, xpath=None):
        pass

    @abstractmethod
    def fill_password(self, xpath=None):
        pass

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
