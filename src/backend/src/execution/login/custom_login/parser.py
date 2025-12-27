import traceback

from lark import Lark, Transformer, LarkError
from lark.exceptions import VisitError

from execution.login.constants import LoginStatusCode
from execution.login.custom_login.custom_login_methods_interfaces import CustomLoginMethodsInterface
from utils.exceptions import ScriptExecutionStopped

grammar = r"""
// Entry point: a sequence of commands
start: stmt*

// All possible statements (commands)
stmt: click_submit_button
    | fill_username
    | fill_password
    | fill_text
    | click_button
    | open_url
    | wait

// Commands with optional string argument
click_submit_button : "clickSubmitButton" "(" [STRING] ")"
fill_username       : "fillUsername" "(" [STRING] ")"
fill_password       : "fillPassword" "(" [STRING] ")"

// Command with two string arguments: fillText("some xpath", "value")
fill_text           : "fillText" "(" STRING "," STRING ")"

// Command with required string argument: clickButton("some string")
click_button        : "clickButton" "(" STRING ")"
open_url            : "openUrl" "(" STRING ")"

// Command with required integer argument: wait(200)
wait                : "wait" "(" INT ")"

// Terminals
%import common.ESCAPED_STRING -> STRING
%import common.INT
%import common.WS

%ignore WS
"""

parser = Lark(grammar, start="start")


class Executor(Transformer):
    def __init__(self, custom_login_methods: CustomLoginMethodsInterface):
        super().__init__()
        self._custom_login_methods = custom_login_methods

    def STRING(self, token):
        # ESCAPED_STRING includes quotes -> strip them
        return token[1:-1]

    def INT(self, token):
        return int(token)

    def click_submit_button(self, items):
        xpath = items[0] if items else None
        self._custom_login_methods.click_submit_button(xpath)

    def fill_username(self, items):
        xpath = items[0] if items else None
        self._custom_login_methods.fill_username(xpath)

    def fill_password(self, items):
        xpath = items[0] if items else None
        self._custom_login_methods.fill_password(xpath)

    def fill_text(self, items):
        xpath, value = items
        self._custom_login_methods.fill_text(xpath, value)

    def click_button(self, items):
        (xpath,) = items
        self._custom_login_methods.click_button(xpath)

    def open_url(self, items):
        (url,) = items
        self._custom_login_methods.open_url(url)

    def wait(self, items):
        (ms,) = items
        self._custom_login_methods.wait(ms)


class CustomLoginScriptParser:
    def __init__(self, custom_login_methods: CustomLoginMethodsInterface):
        self._custom_login_methods = custom_login_methods

    @staticmethod
    def check_syntax(script: str) -> str | None:
        """
        Checks if the syntax of the custom login script is valid. Returns None when valid.
        :param script: The custom login script to parse.
        :return: Returns error message when not valid
        """
        try:
            parser.parse(script)
        except LarkError as e:
            return str(e)
        return None

    def execute(self, script: str) -> ScriptExecutionStopped | None:
        """
        Executes the custom login script.
        """
        tree = parser.parse(script)
        executor = Executor(self._custom_login_methods)
        try:
            executor.transform(tree)
        except VisitError as e:
            orig = e.orig_exc
            if orig is not None and type(orig).__name__ == "ScriptExecutionStopped":
                return orig
            traceback.print_exc()
            return ScriptExecutionStopped()
        except Exception:
            traceback.print_exc()
            return ScriptExecutionStopped()
        return None
