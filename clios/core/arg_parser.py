from abc import ABC, abstractmethod
from dataclasses import dataclass

from .parameter import Parameters, ParamVal


class OprArgParserError(Exception):
    def __init__(self, message: str, string: str = "", spos: int = -1, epos: int = 0):
        """
        An exception to represent an error in parsing operator arguments

        Args:
            message (str): The error message
            string (str): The string being parsed
            spos (int): The start position of the error substring
            epos (int): The end position of the error substring
        """
        self.message = message
        self.string = string
        self.spos = spos
        self.epos = epos
        super().__init__(self.message)


@dataclass(frozen=True)
class OprArgParserAbc(ABC):
    @abstractmethod
    def parse(self, string: str, parameters: Parameters) -> tuple[ParamVal, ...]:
        """
        Operator argument parser interface

        Parse a parameter string into args and kwds

        Args:
            string (str): The parameter string to parse
            parameters: The list of parameters to parse the string into

        Returns:
            tuple[tuple[str, ...], tuple[KWd, ...]]: A tuple containing a tuple of args and a tuple of kwds

        Raises:
            OprArgParserError: If the parameter string is invalid
        """
        pass

    @abstractmethod
    def synopsis(self, parameters: Parameters) -> str:
        pass
