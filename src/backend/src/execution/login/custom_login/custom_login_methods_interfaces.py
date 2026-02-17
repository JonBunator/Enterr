from abc import ABC, abstractmethod


class CustomLoginMethodsInterface(ABC):
    @abstractmethod
    async def click_submit_button(self, xpath=None):
        """
        Clicks the submit button.
        :param xpath: Optional xpath to reference button, when none is set, the system tries to find it automatically.
        """
        pass

    @abstractmethod
    async def fill_username(self, xpath=None):
        """
        Fills the username in the username field.
        :param xpath: Optional xpath to reference text field, when none is set, the system tries to find it automatically.
        """
        pass

    @abstractmethod
    async def fill_password(self, xpath=None):
        """
        Fills the password in the password field.
        :param xpath: Optional xpath to reference text field, when none is set, the system tries to find it automatically.
        """
        pass

    @abstractmethod
    async def fill_text(self, xpath, value):
        """
        Fills a text field with a value.
        :param xpath: The xpath to reference the text field.
        :param value: The new value of the text field that should be set.
        """
        pass

    @abstractmethod
    async def click_button(self, xpath: str):
        """
        Clicks a button with xpath.
        :param xpath: The xpath to reference the button.
        """
        pass

    @abstractmethod
    async def open_url(self, url: str):
        """
        Navigates to the page URL.
        :param url: The URL to navigate to.
        """
        pass

    @abstractmethod
    async def wait(self, ms: int):
        """
        Pauses the executions for a specified time.
        :param ms: Time in milliseconds.
        """
        pass
