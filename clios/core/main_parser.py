import typing as t
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .operator import RootOperator


class ParserError(Exception):
    def __init__(
        self,
        message: str,
        ctx: dict[str, t.Any] = {},
    ) -> None:
        """
        An exception to represent an error in parsing operator arguments

        """
        self.message = message
        self.ctx = ctx
        super().__init__(self.message)


@dataclass(frozen=True)
class ParserAbc(ABC):
    @abstractmethod
    def get_operator(self, input: t.Any, **kwds: t.Any) -> RootOperator:
        """
        Parse the tokens and get the tree of operators

        Args:
            tokens (list[Token]): The tokens to parse

        Returns:
            BaseOperator: The operator
        """

    @abstractmethod
    def get_synopsis(self, operator_name: str) -> str:
        """
        Get the synopsis of an operator

        Args:
            operator_name (str): The operator name

        Returns:
            str: The synopsis
        """
