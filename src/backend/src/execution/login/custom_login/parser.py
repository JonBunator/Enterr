import ast
import traceback

from lark import Lark, Transformer, LarkError
from lark.exceptions import VisitError
from execution.login.custom_login.custom_login_methods_interfaces import (
    CustomLoginMethodsInterface,
)
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
STRING              : "\"" _STRING_ESC_INNER "\"" | "'" _STRING_ESC_INNER "'"
%import common._STRING_ESC_INNER
%import common.INT
%import common.WS

%ignore WS
"""

parser = Lark(grammar, start="start")


class Executor(Transformer):
    """Transforms the parse tree into a list of (method_name, args) tuples."""

    def __init__(self):
        super().__init__()
        self.operations = []

    def STRING(self, token):
        return ast.literal_eval(token)

    def INT(self, token):
        return int(token)

    def click_submit_button(self, items):
        xpath = items[0] if items else None
        self.operations.append(("click_submit_button", (xpath,)))

    def fill_username(self, items):
        xpath = items[0] if items else None
        self.operations.append(("fill_username", (xpath,)))

    def fill_password(self, items):
        xpath = items[0] if items else None
        self.operations.append(("fill_password", (xpath,)))

    def fill_text(self, items):
        xpath, value = items
        self.operations.append(("fill_text", (xpath, value)))

    def click_button(self, items):
        (xpath,) = items
        self.operations.append(("click_button", (xpath,)))

    def open_url(self, items):
        (url,) = items
        self.operations.append(("open_url", (url,)))

    def wait(self, items):
        (ms,) = items
        self.operations.append(("wait", (ms,)))


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

    async def execute(self, script: str) -> ScriptExecutionStopped | None:
        """
        Executes the custom login script.
        """
        tree = parser.parse(script)
        executor = Executor()
        try:
            executor.transform(tree)
            # Execute operations sequentially
            for method_name, args in executor.operations:
                method = getattr(self._custom_login_methods, method_name)
                await method(*args)
        except ScriptExecutionStopped as e:
            return e
        except Exception:
            traceback.print_exc()
            return ScriptExecutionStopped()
        return None
