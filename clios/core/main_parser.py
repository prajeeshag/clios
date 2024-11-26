import typing as t
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .operator import RootOperator
from .operator_fn import OperatorFn, OperatorFns


class ParserErrorCtx(t.TypedDict, total=False):
    token_index: int
    num_extra_tokens: int
    unchainable_token_index: int
    error: Exception


class ParserError(Exception):
    def __init__(
        self,
        message: str,
        ctx: ParserErrorCtx = {},
    ) -> None:
        """
        An exception to represent an error in parsing operator arguments

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
class ParserAbc(ABC):
    @abstractmethod
    def get_operator(
        self, operator_fns: OperatorFns, input: t.Any, **kwds: t.Any
    ) -> RootOperator:
        """
        Parse the tokens and get the tree of operators

        Args:
            operator_fns (OperatorFns): Dictionary of operator functions
            input (t.Any): The input to be parsed
        Returns:
            BaseOperator: The operator
        """

    @abstractmethod
    def get_synopsis(self, operator_fn: OperatorFn, operator_name: str) -> str:
        """
        Get the synopsis of an operator

        Args:
            operator_name (str): The operator name

        Returns:
            str: The synopsis
        """
