from typing import Any, Callable

from .operation import WriteOperation
from .operator import operator_factory, reader_factory, writer_factory
from .parser import Parser
from .registry import OperatorRegistry, ReaderRegistry, WriterRegistry
from .tokenizer import tokenize


class Clios:
    def __init__(self) -> None:
        self._operators = OperatorRegistry()
        self._readers = ReaderRegistry()
        self._writers = WriterRegistry()

    def operator(self, name: str = "") -> Any:
        def decorator(func: Callable[..., Any]):
            op_obj = operator_factory(func)
            key = name if name else func.__name__
            self._operators.add(key, op_obj)
            return func

        return decorator

    def writer(self) -> Any:
        def decorator(func: Callable[..., Any]):
            writer_obj = writer_factory(func)
            self._writers.add(writer_obj.dtype, writer_obj)
            return func

        return decorator

    def reader(self) -> Any:
        def decorator(func: Callable[..., Any]):
            reader_obj = reader_factory(func)
            self._readers.add(reader_obj.dtype, reader_obj)
            return func

        return decorator

    def parse_args(self, args: list[str]) -> WriteOperation:
        parser = Parser(self._operators, self._writers, self._readers)
        tokens = tokenize(args)
        return parser.parse_tokens(tokens)
