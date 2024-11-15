import sys
from operator.utils import get_operator_fn
from typing import Any, Callable

from .ast_builder import ASTBuilder
from .registry import OperatorRegistry
from .tokenizer import tokenize


class Clios:
    def __init__(self) -> None:
        self._operators = OperatorRegistry()

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
