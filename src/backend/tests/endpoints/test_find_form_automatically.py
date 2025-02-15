import os
import pytest
from lxml.etree import HTML

from execution.login.find_form_automatically import find_login_automatically


# Gather the file names to pass as parameters
def get_file_names():
    current_dir = os.path.dirname(__file__)
    examples_dir = os.path.join(current_dir, "login_html_examples")
    return [f for f in os.listdir(examples_dir) if os.path.isfile(os.path.join(examples_dir, f))]


@pytest.mark.parametrize("filename", get_file_names())
def test_find_login_automatically(filename):
    current_dir = os.path.dirname(__file__)
    examples_dir = os.path.join(current_dir, "login_html_examples")
    filepath = os.path.join(examples_dir, filename)

    with open(filepath, 'r') as file:
        content = file.read()
        xpaths = find_login_automatically(content, False)
        assert xpaths is not None, f"Found no xpath for login {filename}"

        dom = HTML(content)
        username_element = dom.xpath(xpaths.username)
        assert len(username_element) == 1, f"Found no username element for login {filename}"
        assert username_element[0].get("test-id") == "username", f"Found wrong username element for login {filename}"

        password_element = dom.xpath(xpaths.password)
        assert len(password_element) == 1, f"Found no password element for login {filename}"
        assert password_element[0].get("test-id") == "password", f"Found wrong password element for login {filename}"

        submit_button_element = dom.xpath(xpaths.submit_button)
        assert len(submit_button_element) == 1, f"Found no submit button element for login {filename}"
        assert submit_button_element[0].get(
            "test-id") == "submit-button", f"Found wrong submit button element for login {filename}"
