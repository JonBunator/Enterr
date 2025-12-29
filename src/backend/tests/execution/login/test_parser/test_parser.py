import pytest

from src.execution.login.constants import LoginStatusCode
from src.execution.login.custom_login.parser import CustomLoginScriptParser
from src.execution.login.custom_login.custom_login_methods_interfaces import (
    CustomLoginMethodsInterface,
)
from src.utils.exceptions import ScriptExecutionStopped


class MockCustomLoginMethods(CustomLoginMethodsInterface):
    """Mock implementation of CustomLoginMethodsInterface for testing"""

    def __init__(self):
        self.calls = []

    def click_submit_button(self, xpath=None):
        self.calls.append(("click_submit_button", xpath))

    def fill_username(self, xpath=None):
        self.calls.append(("fill_username", xpath))

    def fill_password(self, xpath=None):
        self.calls.append(("fill_password", xpath))

    def fill_text(self, xpath, value):
        self.calls.append(("fill_text", xpath, value))

    def click_button(self, xpath: str):
        self.calls.append(("click_button", xpath))

    def open_url(self, url: str):
        self.calls.append(("open_url", url))

    def wait(self, ms: int):
        self.calls.append(("wait", ms))


class TestCustomLoginScriptParser:
    """Test suite for CustomLoginScriptParser"""

    @pytest.fixture
    def mock_methods(self):
        """Create a fresh mock methods instance for each test"""
        return MockCustomLoginMethods()

    @pytest.fixture
    def parser(self, mock_methods):
        """Create a parser instance with mock methods"""
        return CustomLoginScriptParser(mock_methods)

    def test_check_syntax_empty_script(self):
        """Test that an empty script is valid"""
        result = CustomLoginScriptParser.check_syntax("")
        assert result is None

    def test_check_syntax_valid_single_command(self):
        """Test that a single valid command passes syntax check"""
        result = CustomLoginScriptParser.check_syntax("clickSubmitButton()")
        assert result is None

    def test_check_syntax_valid_multiple_commands(self):
        """Test that multiple valid commands pass syntax check"""
        script = """
        fillUsername()
        fillPassword()
        clickSubmitButton()
        """
        result = CustomLoginScriptParser.check_syntax(script)
        assert result is None

    def test_check_syntax_invalid_command(self):
        """Test that an invalid command returns an error"""
        result = CustomLoginScriptParser.check_syntax("invalidCommand()")
        assert result is not None
        assert isinstance(result, str)

    def test_check_syntax_missing_parentheses(self):
        """Test that missing parentheses returns an error"""
        result = CustomLoginScriptParser.check_syntax("clickSubmitButton")
        assert result is not None

    def test_check_syntax_invalid_argument_type(self):
        """Test that invalid argument types return an error"""
        result = CustomLoginScriptParser.check_syntax('wait("not a number")')
        assert result is not None

    def test_check_syntax_missing_comma_in_fill_text(self):
        """Test that missing comma in fillText returns an error"""
        result = CustomLoginScriptParser.check_syntax('fillText("xpath" "value")')
        assert result is not None

    # Execution tests for clickSubmitButton

    def test_execute_click_submit_button_no_args(self, parser, mock_methods):
        """Test executing clickSubmitButton without arguments"""
        script = "clickSubmitButton()"
        parser.execute(script)
        assert mock_methods.calls == [("click_submit_button", None)]

    def test_execute_click_submit_button_with_xpath(self, parser, mock_methods):
        """Test executing clickSubmitButton with xpath"""
        script = "clickSubmitButton(\"//button[@id='submit']\")"
        parser.execute(script)
        assert mock_methods.calls == [("click_submit_button", "//button[@id='submit']")]

    # Execution tests for fillUsername

    def test_execute_fill_username_no_args(self, parser, mock_methods):
        """Test executing fillUsername without arguments"""
        script = "fillUsername()"
        parser.execute(script)
        assert mock_methods.calls == [("fill_username", None)]

    def test_execute_fill_username_with_xpath(self, parser, mock_methods):
        """Test executing fillUsername with xpath"""
        script = "fillUsername(\"//input[@name='username']\")"
        parser.execute(script)
        assert mock_methods.calls == [("fill_username", "//input[@name='username']")]

    # Execution tests for fillPassword

    def test_execute_fill_password_no_args(self, parser, mock_methods):
        """Test executing fillPassword without arguments"""
        script = "fillPassword()"
        parser.execute(script)
        assert mock_methods.calls == [("fill_password", None)]

    def test_execute_fill_password_with_xpath(self, parser, mock_methods):
        """Test executing fillPassword with xpath"""
        script = "fillPassword(\"//input[@type='password']\")"
        parser.execute(script)
        assert mock_methods.calls == [("fill_password", "//input[@type='password']")]

    # Execution tests for fillText

    def test_execute_fill_text(self, parser, mock_methods):
        """Test executing fillText with xpath and value"""
        script = 'fillText("//input[@id=\'email\']", "test@example.com")'
        parser.execute(script)
        assert mock_methods.calls == [
            ("fill_text", "//input[@id='email']", "test@example.com")
        ]

    # Execution tests for clickButton

    def test_execute_click_button(self, parser, mock_methods):
        """Test executing clickButton with xpath"""
        script = "clickButton(\"//button[@class='login-btn']\")"
        parser.execute(script)
        assert mock_methods.calls == [("click_button", "//button[@class='login-btn']")]

    # Execution tests for openUrl

    def test_execute_open_url(self, parser, mock_methods):
        """Test executing openUrl"""
        script = 'openUrl("https://example.com/login")'
        parser.execute(script)
        assert mock_methods.calls == [("open_url", "https://example.com/login")]

    # Execution tests for wait

    def test_execute_wait(self, parser, mock_methods):
        """Test executing wait with milliseconds"""
        script = "wait(1000)"
        parser.execute(script)
        assert mock_methods.calls == [("wait", 1000)]

    def test_wait_missing_argument(self):
        """Test that wait without argument is invalid"""
        result = CustomLoginScriptParser.check_syntax("wait()")
        assert result is not None

    # Error handling tests

    def test_execute_script_execution_stopped(self):
        """Test that ScriptExecutionStopped exception is caught and returned"""

        class ExceptionRaisingMock(CustomLoginMethodsInterface):
            def fill_username(self, xpath=None):
                raise ScriptExecutionStopped(
                    status=LoginStatusCode.USERNAME_FIELD_NOT_FOUND, message="Test stop"
                )

            def fill_password(self, xpath=None):
                pass

            def click_submit_button(self, xpath=None):
                pass

            def fill_text(self, xpath, value):
                pass

            def click_button(self, xpath: str):
                pass

            def open_url(self, url: str):
                pass

            def wait(self, ms: int):
                pass

        mock_methods = ExceptionRaisingMock()
        parser = CustomLoginScriptParser(mock_methods)

        script = "fillUsername()"
        result = parser.execute(script)

        assert result is not None
        assert type(result).__name__ == "ScriptExecutionStopped"
        assert result.message == "Test stop"
        assert result.status == LoginStatusCode.USERNAME_FIELD_NOT_FOUND

    # Edge case tests

    def test_execute_whitespace_handling(self, parser, mock_methods):
        """Test that various whitespace patterns are handled correctly"""
        script = """
        
        
        fillUsername()
        
        fillPassword()
        
        
        """
        parser.execute(script)
        assert len(mock_methods.calls) == 2

    def test_execute_no_whitespace(self, parser, mock_methods):
        """Test script execution without whitespace between commands"""
        script = "fillUsername()fillPassword()clickSubmitButton()"
        parser.execute(script)
        assert len(mock_methods.calls) == 3

    def test_string_with_escaped_quotes(self, parser, mock_methods):
        """Test that escaped quotes in strings are handled correctly"""
        script = r'fillText("//input", "value with \"escaped\" quotes")'
        parser.execute(script)
        assert len(mock_methods.calls) == 1
        assert mock_methods.calls[0][0] == "fill_text"

    def test_url_with_query_params(self, parser, mock_methods):
        """Test that URLs with query parameters are handled correctly"""
        script = 'openUrl("https://example.com/login?redirect=/dashboard&foo=bar")'
        parser.execute(script)
        assert mock_methods.calls == [
            ("open_url", "https://example.com/login?redirect=/dashboard&foo=bar")
        ]

    def test_xpath_with_complex_expression(self, parser, mock_methods):
        """Test that complex XPath expressions are handled correctly"""
        script = "clickButton(\"//div[@class='container']//button[contains(text(), 'Login')]\")"
        parser.execute(script)
        assert mock_methods.calls == [
            (
                "click_button",
                "//div[@class='container']//button[contains(text(), 'Login')]",
            )
        ]

    def test_string_parsing(self, parser, mock_methods):
        """Test that string are parsed correctly with different quote styles"""
        script = """
        fillUsername('"')
        fillUsername('\\'')
        fillUsername("'")
        fillUsername("\\"")
        """
        parser.execute(script)
        assert mock_methods.calls == [
            ("fill_username", '"'),
            ("fill_username", "'"),
            ("fill_username", "'"),
            ("fill_username", '"'),
        ]
