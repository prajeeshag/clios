import typing as t
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .parameter import Parameters


class ParamParserErrorCtx(t.TypedDict, total=False):
    spos: int
    epos: int
    error: Exception


class ParamParserError(Exception):
    def __init__(
        self,
        message: str,
        ctx: ParamParserErrorCtx = {},
    ) -> None:
        """
        An exception to represent an error in parsing operator arguments

        Args:
            message (str): The error message
            string (str): The string being parsed
            spos (int): The start position of the error substring
            epos (int): The end position of the error substring
        """
        self.message = message
        self.ctx = ctx
        super().__init__(self.message)

    def __str__(self) -> str:
        message = self.message
        if "error" in self.ctx:
            message += f"\n{str(self.ctx['error'])}"
        return message


@dataclass(frozen=True)
class ParamParserAbc(ABC):
    """
    An abstract class to represent an operator argument parser
    """

    @abstractmethod
    def parse_arguments(
        self, string: str, parameters: Parameters
    ) -> tuple[tuple[t.Any, ...], tuple[tuple[str, t.Any], ...]]:
        """
        Parse a parameter string into args and kwds

        Args:
            string (str): The parameter string to parse
            parameters: The list of parameters to parse the string into

        Returns:
            tuple[tuple[str, ...], tuple[KWd, ...]]: A tuple containing a tuple of args and a tuple of kwds

        Raises:
            OprArgParserError: If the parameter string is invalid
        """

    @abstractmethod
    def get_synopsis(self, parameters: Parameters) -> str:
        """
        Get the synopsis of the operator arguments

        Args:
            parameters: The list of parameters to get the synopsis for

        Returns:
            str: The synopsis of the operator arguments
        """
