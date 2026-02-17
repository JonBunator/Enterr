import re
from typing import List, Tuple, Dict
from dataclasses import dataclass
from lxml.etree import _Element as Element, HTML
from typing import NewType
from execution.login.dom_interaction.interfaces.dom_interaction_interface import (
    DomInteractionInterface,
)

XPath = NewType("XPath", str)
Score = NewType("Score", int)
Scoring = NewType("Scoring", Dict[Element, Tuple[List[str], Score]])


@dataclass
class XPaths:
    username: XPath | None
    password: XPath | None
    submit_button: XPath | None


class LoginFormFinder:
    def __init__(self, driver: DomInteractionInterface):
        self._driver = driver
        self._dom = None

    async def _init_dom(self):
        html = await self._driver.get_page_html()
        self._dom = HTML(html)

    async def find_login_automatically(self) -> XPaths | None:
        """
        Tries to find the login form automatically and returns the xpath.
        """
        await self._init_dom()

        username_xpath = await self._find_username_field()
        password_xpath = await self._find_password_field()
        submit_button_xpath = await self._find_submit_button()
        if (
            username_xpath is None
            and password_xpath is None
            and submit_button_xpath is None
        ):
            return None
        return XPaths(
            username=username_xpath,
            password=password_xpath,
            submit_button=submit_button_xpath,
        )

    async def _find_username_field(self) -> XPath | None:
        """
        Tries to find xpath of username field automatically.
        """
        tag_scores = [("input", Score(8))]
        id_aliases = ["email", "e-mail", "username", "user", "uid"]
        type_scores = [("email", Score(10)), ("text", Score(1))]
        property_scores = [
            ("@name", Score(10)),
            ("@id", Score(10)),
            ("@class", Score(2)),
            ("@autocomplete", Score(10)),
            ("@placeholder", Score(3)),
        ]
        return await self._find_form_field(
            id_aliases, tag_scores, type_scores, property_scores
        )

    async def _find_password_field(self) -> XPath | None:
        """
        Tries to find xpath of password field automatically.
        """
        tag_scores = [("input", Score(8))]
        id_aliases = ["password", "pwd"]
        type_scores = [("password", Score(10)), ("text", Score(1))]
        property_scores = [
            ("@name", Score(10)),
            ("@id", Score(10)),
            ("@class", Score(2)),
            ("@autocomplete", Score(10)),
            ("@placeholder", Score(3)),
        ]
        return await self._find_form_field(
            id_aliases, tag_scores, type_scores, property_scores
        )

    async def _find_submit_button(self) -> XPath | None:
        """
        Tries to find xpath of submit button automatically.
        """
        tag_scores = [("button", Score(8)), ("input", Score(8)), ("div", Score(1))]
        id_aliases = [
            "login",
            "log in",
            "log-in",
            "signin",
            "sign in",
            "sign-in",
            "submit",
        ]
        type_scores = [("submit", Score(30)), ("button", Score(10))]
        property_scores = [
            ("@name", Score(10)),
            ("@id", Score(10)),
            ("@class", Score(2)),
            ("@value", Score(3)),
            ("text()", Score(10)),
        ]
        return await self._find_form_field(
            id_aliases, tag_scores, type_scores, property_scores
        )

    async def _find_form_field(
        self,
        id_aliases: List[str],
        tag_scores: List[Tuple[str, Score]],
        type_scores: List[Tuple[str, Score]],
        property_scores: List[Tuple[str, Score]],
    ) -> XPath | None:
        """
        Tries to find xpath of form field automatically.
        @param tag_types: The tag types to search for. For example input, div, span etc.
        @param id_aliases: Aliases to search for in dom that are used for property values.
        @param type_scores: List of tuples (type, score). Maps type to score. Types are for example submit, button, password etc.
        @param property_scores: List of tuples (xpath_property_selector, score). Maps xpath_property_selector to score. Properties are value, name, id etc.
        @return: XPaths object. None if no element is found.
        """
        selector_scoring = {}
        selector_scoring = self._find_by_tag(selector_scoring, tag_scores)
        for i, (tag_type, tag_score) in enumerate(tag_scores):
            selector_scoring = self._find_by_type(
                selector_scoring, tag_type, type_scores
            )
            selector_scoring = self._find_by_property(
                selector_scoring, tag_type, id_aliases, property_scores
            )
            selector_scoring = self._find_by_dom_text(
                selector_scoring, tag_type, id_aliases
            )

        selector_scoring = self._remove_if_hidden(selector_scoring)
        selector_scoring = self._find_by_form_child(selector_scoring)
        # Get element with the highest score
        return await self._find_best_element(selector_scoring)

    async def _find_best_element(self, scoring: Scoring) -> XPath | None:
        if not scoring:
            return None

        best_element = max(scoring, key=lambda x: scoring[x][1], default=None)
        if best_element is None:
            return None
        xpath = best_element.getroottree().getpath(best_element)
        if await self._driver.is_element_visible(xpath):
            return XPath(xpath)

        # Best element is not visible -> remove from scoring
        del scoring[best_element]
        return await self._find_best_element(scoring)

    def _find_by_tag(
        self, scoring: Scoring, tag_scores: List[Tuple[str, Score]]
    ) -> Scoring:
        """
        Finds element by tag and adds it to the scoring dictionary.
        """
        for tag_type, score in tag_scores:
            scoring = self._find_element(scoring, XPath(f"//{tag_type}"), score)
        return scoring

    def _find_by_type(
        self, scoring: Scoring, tag_type: str, type_scores: List[Tuple[str, Score]]
    ) -> Scoring:
        """
        Finds element by type and adds it to the scoring dictionary.
        """
        for input_type, score in type_scores:
            scoring = self._find_element(
                scoring, XPath(f"//{tag_type}[@type='{input_type}']"), score
            )
        return scoring

    def _find_by_property(
        self,
        scoring: Scoring,
        tag_type: str,
        id_aliases: List[str],
        property_scores: List[Tuple[str, Score]],
    ) -> Scoring:
        """
        Finds element by property and adds it to the scoring dictionary.
        """
        for alias in id_aliases:
            for prop, score in property_scores:
                xpath = f"//{tag_type}[{prop}]"
                elements = self._dom.xpath(xpath)
                for element in elements:
                    prop_val = re.sub(r"[^a-zA-Z]", "", prop)
                    if prop_val == "text":
                        value = element.text
                    else:
                        value = element.get(prop_val)
                    if value is None:
                        continue
                    if alias in value.lower():
                        if "'" in value or '"' in value:
                            continue
                        scoring = self._find_element(
                            scoring, XPath(f"//{tag_type}[{prop} = '{value}']"), score
                        )
        return scoring

    def _find_by_dom_text(
        self, scoring: Scoring, tag_type: str, id_aliases: List[str]
    ) -> Scoring:
        """
        Finds elements in dom hierarchy that contains text, which is used to label input and adds it to the scoring dictionary.
        """
        inputs = self._dom.xpath(f"//{tag_type}")
        for i, input_field in enumerate(inputs):

            def _element_contains_text(element: Element, element_scoring: Scoring):
                """
                Add element to scoring if text contains any of the id aliases.
                """
                if element is None or element.text is None:
                    return
                if any(substring in element.text.lower() for substring in id_aliases):
                    scoring = self._find_element(
                        element_scoring, XPath(f"(//{tag_type})[{i + 1}]"), Score(2)
                    )

            parent = input_field.getparent()
            # Find parent that has only input as children and no other inputs
            while parent is not None:
                grandparent = parent.getparent()
                if grandparent is None or len(grandparent.xpath(f".//{tag_type}")) > 1:
                    break
                parent = parent.getparent()

            _element_contains_text(parent, scoring)
            for child in parent.iterchildren():
                if child.text is not None:
                    _element_contains_text(child, scoring)
        return scoring

    def _find_by_form_child(self, scoring: Scoring):
        """
        Logins are often inside a form. Score high when child of form element.
        """
        for element in scoring:
            xpath = element.getroottree().getpath(element)
            if "form" in xpath:
                scoring = self._add_score_to_element(
                    element, scoring, xpath, Score(100)
                )
        return scoring

    def _find_element(self, scoring: Scoring, xpath: XPath, score: Score) -> Scoring:
        """
        Finds element in dom using xpath and adds a score.
        """
        elements = self._dom.xpath(xpath)
        for element in elements:
            self._add_score_to_element(element, scoring, xpath, score)
        return scoring

    def _add_score_to_element(
        self, element: Element, scoring: Scoring, xpath: str, score: int
    ):
        """
        Adds a score to an element.
        """
        if element in scoring:
            xpaths = scoring[element][0]
            if xpath in xpaths:
                return
            xpaths.append(xpath)
            scoring[element] = (xpaths, scoring[element][1] + score)
        else:
            scoring[element] = ([xpath], score)
        return scoring

    def _remove_if_hidden(self, scoring: Scoring) -> Scoring:
        """
        Ignore elements that are hidden.
        """
        for element in list(scoring.keys()):
            if element.get("hidden") is not None or element.get("type") == "hidden":
                scoring.pop(element)
        return scoring
