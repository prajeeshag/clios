import enum
import typing as t
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from .operator import RootOperator
from .operator_fn import OperatorFn, OperatorFns


class _KnownTypes(enum.Enum):
    INT = int
    FLOAT = float
    TEXT = str
    BOOL = bool
    DATETIME = datetime
    DATE = date
    TIME = time
    TIMDELTA = timedelta

    @classmethod
    def _missing_(cls, value: t.Any) -> t.Any:
        return cls.TEXT  # pragma: no cover


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
    def is_inline_operator_name(self, name: str) -> bool:
        """
        Check if the string name is an inline operator
        """

    @abstractmethod
    def get_inline_operator_fn(self, name: str, index: int) -> OperatorFn:
        """
        Get an inline operator function

        Args:
            name (str): The operator name
            index (int): The index of the operator

        Returns:
            OperatorFn: The operator function
        """

    @abstractmethod
    def get_synopsis(
        self,
        operator_fn: OperatorFn,
        operator_name: str,
        **kwds: t.Any,
    ) -> str:
        """
        Get the synopsis of an operator

        Args:
            operator_name (str): The operator name

        Returns:
            str: The synopsis
        """

    def get_details(
        self,
        name: str,
        op_fn: OperatorFn,
        exe_name: str = "",
    ) -> tuple[
        str,
        str,
        str,
        list[dict[str, str]],
        list[dict[str, str]],
    ]:
        """
        Get the details of an operator

        Args:
            name (str): The operator name
            op_fn (OperatorFn): The operator function
            exe_name (str, optional): The executable name. Defaults to "".

        Returns:
           synopsis, short_description, long_description, args_doc, kwds_doc
        """

        synopsis = self.get_synopsis(op_fn, name)

        if exe_name:
            synopsis = f"{exe_name}{synopsis}"

        short_description = op_fn.short_description
        long_description = op_fn.long_description
        args_doc: list[dict[str, str]] = []
        kwds_doc: list[dict[str, str]] = []
        for param in op_fn.parameters:
            if param.is_positional_param or param.is_var_param:
                docs = args_doc
            elif param.is_keyword_param or param.is_var_keyword:
                docs = kwds_doc
            else:
                continue
            doc: dict[str, t.Any] = {}
            doc["name"] = param.name
            doc["type"] = _KnownTypes(param.type_).name
            doc["required"] = "Required" if param.is_required else "Optional"
            doc["default_value"] = str(param.default)
            if param.default == "":
                doc["default_value"] = "''"
            if param.default is param.empty:
                doc["default_value"] = ""
            doc["description"] = param.description
            doc["choices"] = ""
            if param.choices:
                doc["choices"] = ", ".join(param.choices)
            docs.append(doc)
        return synopsis, short_description, long_description, args_doc, kwds_doc
