import re
from typing import List, Tuple, Dict
from lxml import etree
from dataclasses import dataclass
from lxml.etree import _Element as Element, HTML
from typing import NewType
from .selenium_adapter import SeleniumDriver

XPath = NewType('XPath', str)
Score = NewType('Score', int)
Scoring = NewType('Scoring', Dict[Element, Tuple[List[str], Score]])

@dataclass
class XPaths:
    username: XPath
    password: XPath
    pin: XPath
    submit_button: XPath


def find_login_automatically(sd: SeleniumDriver, html: str, pin_used: bool) -> XPaths | None:
    """
    Tries to find the login form automatically and returns the xpath.
    @param html: The html that is used for parsing.
    @return: XPaths object. None if no form is found.
    """
    dom = HTML(html)
    username_xpath = _find_username_field(sd, dom)
    password_xpath = _find_password_field(sd, dom)
    if pin_used:
        pin_xpath = _find_pin_field(sd, dom)
    else:
        pin_xpath = None
    submit_button_xpath = _find_submit_button(sd, dom)
    if username_xpath is None and password_xpath and None and submit_button_xpath is None:
        return None
    return XPaths(username=username_xpath, password=password_xpath, pin=pin_xpath, submit_button=submit_button_xpath)


def _find_username_field(sd: SeleniumDriver, dom: HTML) -> XPath | None:
    """
    Tries to find xpath of username field automatically.
    """
    tag_types = ["input"]
    id_aliases = ["email", "e-mail", "username", "user", "uid"]
    type_scores = [("email", Score(10)), ("text", Score(1))]
    property_scores = [("@name", Score(10)), ("@id", Score(10)), ("@class", Score(10)), ("@autocomplete", Score(10)), ("@placeholder", Score(3))]
    return _find_form_field(sd, dom, tag_types, id_aliases, type_scores, property_scores)


def _find_password_field(sd: SeleniumDriver, dom: etree.HTML) -> XPath | None:
    """
    Tries to find xpath of password field automatically.
    """
    tag_types = ["input"]
    id_aliases = ["password", "pwd"]
    type_scores = [("password", Score(10)), ("text", Score(1))]
    property_scores = [("@name", Score(10)), ("@id", Score(10)), ("@class", Score(10)), ("@autocomplete", Score(10)), ("@placeholder", Score(3))]
    return _find_form_field(sd, dom, tag_types, id_aliases, type_scores, property_scores)


def _find_pin_field(sd: SeleniumDriver, dom: HTML) -> XPath | None:
    """
    Tries to find xpath of pin field automatically.
    """
    tag_types = ["input"]
    id_aliases = ["pin"]
    type_scores = [("number", Score(10)), ("text", Score(1))]
    property_scores = [("@name", Score(10)), ("@id", Score(10)), ("@class", Score(10)), ("@autocomplete", Score(10)), ("@placeholder", Score(3))]
    return _find_form_field(sd, dom, tag_types, id_aliases, type_scores, property_scores)


def _find_submit_button(sd: SeleniumDriver, dom: HTML) -> XPath | None:
    """
    Tries to find xpath of submit button automatically.
    """
    tag_types = ["button", "input", "div"]
    id_aliases = ["login", "log in", "log-in", "signin", "sign in", "sign-in", "submit"]
    type_scores = [("submit", Score(10)), ("button", Score(10))]
    property_scores = [("@name", Score(10)), ("@id", Score(10)), ("@class", Score(10)), ("@value", Score(3)), ("text()", Score(10))]
    return _find_form_field(sd, dom, tag_types, id_aliases, type_scores, property_scores)


def _find_form_field(sd: SeleniumDriver, dom: HTML, tag_types: List[str], id_aliases: List[str], type_scores: List[Tuple[str, Score]], property_scores: List[Tuple[str, Score]]) -> XPath | None:
    """
    Tries to find xpath of form field automatically.
    @param dom: The lxml dom that is used for parsing.
    @param tag_types: The tag types to search for. For example input, div, span etc.
    @param id_aliases: Aliases to search for in dom that are used for property values.
    @param type_scores: List of tuples (type, score). Maps type to score. Types are for example submit, button, password etc.
    @param property_scores: List of tuples (xpath_property_selector, score). Maps xpath_property_selector to score. Properties are value, name, id etc.
    @return: XPaths object. None if no element is found.
    """
    selector_scoring = {}
    for i, tag_type in enumerate(tag_types):
        selector_scoring = _find_by_type(dom, selector_scoring, tag_type, type_scores)
        selector_scoring = _find_by_property(dom, selector_scoring, tag_type, id_aliases, property_scores)
        selector_scoring = _find_by_dom_text(dom, selector_scoring, tag_type, id_aliases)

    selector_scoring = _remove_if_hidden(selector_scoring)

    # Get element with the highest score
    return _find_best_element(sd, selector_scoring)


def _find_best_element(sd: SeleniumDriver, scoring: Scoring) -> XPath | None:
    if not scoring:
        return None

    best_element = max(scoring, key=lambda x: scoring[x][1], default=None)
    if best_element is None:
        return None
    xpath = best_element.getroottree().getpath(best_element)
    if sd.is_element_visible(xpath):
        return XPath(xpath)

    # Best element is not visible -> remove from scoring
    del scoring[best_element]
    return _find_best_element(sd, scoring)


def _find_by_type(dom: etree.HTML, scoring: Scoring, tag_type: str, type_scores: List[Tuple[str, Score]]) -> Scoring:
    """
    Finds element by type and adds it to the scoring dictionary.
    """
    for input_type, score in type_scores:
        scoring = _find_element(dom, scoring, XPath(f"//{tag_type}[@type='{input_type}']"), score)
    return scoring


def _find_by_property(dom: HTML, scoring: Scoring, tag_type: str, id_aliases: List[str], property_scores: List[Tuple[str, Score]]) -> Scoring:
    """
    Finds element by property and adds it to the scoring dictionary.
    """
    for alias in id_aliases:
        for prop, score in property_scores:
            xpath = f"//{tag_type}[{prop}]"
            elements = dom.xpath(xpath)
            for element in elements:
                prop_val = re.sub(r'[^a-zA-Z]', '', prop)
                if prop_val == "text":
                    value = element.text
                else:
                    value = element.get(prop_val)
                if value is None:
                    continue
                if alias in value.lower():
                    if "'" in value or '"' in value:
                        continue
                    scoring = _find_element(dom, scoring, XPath(f"//{tag_type}[{prop} = '{value}']"), score)
    return scoring


def _find_by_dom_text(dom: HTML, scoring: Scoring, tag_type: str, id_aliases: List[str])-> Scoring:
    """
    Finds elements in dom hierarchy that contains text, which is used to label input and adds it to the scoring dictionary.
    """
    inputs = dom.xpath(f"//{tag_type}")
    for i, input_field in enumerate(inputs):
        def _element_contains_text(element: Element, element_scoring: Scoring):
            """
            Add element to scoring if text contains any of the id aliases.
            """
            if element is None or element.text is None:
                return
            if any(substring in element.text.lower() for substring in id_aliases):
                scoring = _find_element(dom, element_scoring, XPath(f"(//{tag_type})[{i + 1}]"), Score(2))

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


def _find_element(dom: HTML, scoring: Scoring, xpath: XPath, score: Score) -> Scoring:
    """
    Finds element in dom using xpath and adds a score.
    """
    elements = dom.xpath(xpath)
    for element in elements:
        if element in scoring:
            xpaths = scoring[element][0]
            if xpath in xpaths:
                continue
            xpaths.append(xpath)
            scoring[element] = (xpaths, scoring[element][1] + score)
        else:
            scoring[element] = ([xpath], score)
    return scoring


def _remove_if_hidden(scoring: Scoring) -> Scoring:
    """
    Ignore elements that are hidden.
    """
    for element in list(scoring.keys()):
        if element.get("hidden") is not None or element.get("type") == "hidden":
            scoring.pop(element)
    return scoring
