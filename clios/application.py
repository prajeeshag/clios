import sys
from typing import Annotated, Any, Callable

from rich import print

from .ast_builder import ASTBuilder
from .operator.params import Input
from .operator.utils import get_operator_fn
from .registry import OperatorRegistry
from .tokenizer import tokenize


def output(input: Annotated[Any, Input()]) -> None:
    print(input)


class Clios:
    def __init__(self) -> None:
        self._operators = OperatorRegistry()
        self._operators.add("print", get_operator_fn(output))

    def operator(self, name: str = "") -> Any:
        def decorator(func: Callable[..., Any]):
            op_obj = get_operator_fn(func)
            key = name if name else func.__name__
            self._operators.add(key, op_obj)
            return func

        return decorator

    def __call__(self) -> Any:
        ast_builder = ASTBuilder(self._operators)
        tokens = tokenize(sys.argv[1:])
        operator = ast_builder.parse_tokens(tokens)
        return operator.execute()
