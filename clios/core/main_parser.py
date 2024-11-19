import typing as t
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .operator import BaseOperator
from .tokenizer import Token


class ParserError(Exception):
    def __init__(
        self,
        message: str,
        index: str,
        ctx: dict[str, t.Any] = {},
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
        self.index = index
        self.ctx = ctx
        super().__init__(self.message)


@dataclass(frozen=True)
class ParserAbc(ABC):
    @abstractmethod
    def get_name(self, string: str) -> str:
        """
        Get the name of the operator from the string

        Args:
            string (str): The string to get the operator name from

        Returns:
            str: The name of the operator

        Raises:
            OprParserError: If the operator name is invalid
        """

    @abstractmethod
    def get_param_string(self, string: str) -> str:
        """
        Get the parameter string from the operator string

        Args:
            string (str): The string to get the parameter string from

        Returns:
            str: The parameter string
        """

    @abstractmethod
    def get_operator(self, tokens: list[Token]) -> tuple[BaseOperator, ...]:
        """
        Get the inputs from the list of input tokens

        Args:
            tokens (list[Token]): The list of tokens to get the inputs from

        Returns:
            tuple[BaseOperator, ...]: A tuple of the input operators
        """
