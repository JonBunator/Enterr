from abc import abstractmethod
from typing import Optional, Type
from execution.login.dom_interaction.interfaces.dom_interaction_driver_interface import (
    DomInteractionDriverInterface,
)
from execution.login.dom_interaction.interfaces.dom_interaction_methods_interface import (
    DomInteractionMethodsInterface,
)


class DomInteractionInterface(
    DomInteractionMethodsInterface, DomInteractionDriverInterface
):
    def __init__(self, url: str):
        self._url = url

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc: Optional[BaseException], tb
    ) -> Optional[bool]:
        raise NotImplementedError
