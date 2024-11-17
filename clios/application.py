from typing import Annotated, Any, Callable

import click
from rich import print

from clios.operator.operator import RootOperator

from .ast_builder import ASTBuilder
from .cli_docs import print_detail, print_list
from .operator.params import Input
from .operator.utils import Implicit, get_operator_fn
from .registry import OperatorRegistry
from .tokenizer import tokenize


def output(input: Annotated[Any, Input()]) -> None:
    print(input)


@click.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
@click.option("--help", type=str, help="Help message.", default=None, nargs=1)
@click.pass_context
def run_app(ctx: Any, help: str | None, **kwargs: Any) -> None:
    app = ctx.obj
    argv = ctx.args
    if help == "":
        print_list(app._operators)
    elif help:
        try:
            op = app._operators.get(help)
        except KeyError:
            print_list(app._operators)
        else:
            print_detail(help, op)
    elif len(argv) < 1:
        print_list(app._operators)
    else:
        app.run(argv)


class Clios:
    def __init__(self) -> None:
        self._operators = OperatorRegistry()
        self._operators.add("print", get_operator_fn(output))

    def operator(self, name: str = "", implicit: Implicit = "input") -> Any:
        def decorator(func: Callable[..., Any]):
            op_obj = get_operator_fn(func, implicit)
            key = name if name else func.__name__
            self._operators.add(key, op_obj)
            return func

        return decorator

    def run(self, argv: list[str]) -> Any:
        tokens = tokenize(argv)
        ast_builder = ASTBuilder(self._operators)
        operator = ast_builder.parse_tokens(tokens)
        if not isinstance(operator, RootOperator):
            return
        return operator.execute()

    def __call__(self) -> Any:
        return run_app(obj=self)
