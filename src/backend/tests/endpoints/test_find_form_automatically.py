import os
import pytest
from lxml.etree import HTML

from src.execution.login.find_form_automatically import LoginFormFinder
from src.execution.login.dom_interaction.interfaces.dom_interaction_interface import (
    DomInteractionInterface,
)


class MockDomInteractionDriver(DomInteractionInterface):
    """Mock implementation for testing that always returns elements as visible"""

    def __init__(self, html_content: str):
        super().__init__(url="")
        self._html_content = html_content

    def fill_text(self, xpath, value):
        pass

    def click_button(self, xpath):
        pass

    def open_url(self, url):
        pass

    def wait(self, ms):
        pass

    def is_element_visible(self, xpath: str) -> bool:
        return True

    def get_page_html(self) -> str:
        return self._html_content

    def save_screenshot(self, screenshot_id: str):
        pass

    def find_element(self, xpath: str) -> bool:
        return True

    def solve_captcha(self):
        pass

    def disconnect_driver(self):
        pass

    def get_current_url(self) -> str:
        return "http://test.com"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass


# Gather the file names to pass as parameters
def get_file_names():
    current_dir = os.path.dirname(__file__)
    examples_dir = os.path.join(current_dir, "login_html_examples")
    return [
        f
        for f in os.listdir(examples_dir)
        if os.path.isfile(os.path.join(examples_dir, f))
    ]


@pytest.mark.parametrize("filename", get_file_names())
def test_find_login_automatically(filename):
    current_dir = os.path.dirname(__file__)
    examples_dir = os.path.join(current_dir, "login_html_examples")
    filepath = os.path.join(examples_dir, filename)

    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()
        mock_driver = MockDomInteractionDriver(content)
        finder = LoginFormFinder(mock_driver)
        xpaths = finder.find_login_automatically()
        assert xpaths is not None, f"Found no xpath for login {filename}"

        dom = HTML(content)
        username_element = dom.xpath(xpaths.username)

        assert (
            len(username_element) == 1
        ), f"Found no username element for login {filename}"
        assert (
            username_element[0].get("test-id") == "username"
        ), f"Found wrong username element for login {filename}"

        password_element = dom.xpath(xpaths.password)
        assert (
            len(password_element) == 1
        ), f"Found no password element for login {filename}"
        assert (
            password_element[0].get("test-id") == "password"
        ), f"Found wrong password element for login {filename}"

        submit_button_element = dom.xpath(xpaths.submit_button)
        assert (
            len(submit_button_element) == 1
        ), f"Found no submit button element for login {filename}"
        assert (
            submit_button_element[0].get("test-id") == "submit-button"
        ), f"Found wrong submit button element for login {filename}"
