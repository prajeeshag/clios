import sys
from typing import Annotated, Any, Callable

import click
from rich import print

from clios.operator.operator import RootOperator

from .ast_builder import ASTBuilder
from .cli import print_detail, print_list
from .operator.params import Input
from .operator.utils import Implicit, get_operator_fn
from .registry import OperatorRegistry
from .tokenizer import tokenize


def output(input: Annotated[Any, Input()]) -> None:
    """Print the input data to the screen.

    It uses the `rich` library to print the data in a formatted way.
    """
    print(input)


@click.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
@click.option("--list", type=bool, help="List all available operators", is_flag=True)
@click.option(
    "--show", type=str, help="Show the help information for the given operator", nargs=1
)
@click.pass_context
def _click_app(ctx: Any, **kwargs: Any) -> tuple[list[str], dict[str, Any]]:
    return ctx.args, kwargs


class Clios:
    def __init__(self) -> None:
        self.operators = OperatorRegistry()
        self.operators.add("print", get_operator_fn(output))

    def operator(self, name: str = "", implicit: Implicit = "input") -> Any:
        def decorator(func: Callable[..., Any]):
            op_obj = get_operator_fn(func, implicit)
            key = name if name else func.__name__
            self.operators.add(key, op_obj)
            return func

        return decorator

    def run(self, argv: list[str]) -> Any:
        tokens = tokenize(argv)
        ast_builder = ASTBuilder(self.operators)
        operator = ast_builder.parse_tokens(tokens)
        if not isinstance(operator, RootOperator):
            return
        return operator.execute()

    def __call__(self) -> Any:
        try:
            args, options = _click_app(standalone_mode=False)
        except click.exceptions.UsageError as e:
            print(e.format_message())
            sys.exit(1)
        if options["list"]:
            return print_list(self.operators)
        if options["show"] is not None:
            return print_detail(options["show"], self.operators.get(options["show"]))
        if args:
            return self.run(args)

        with click.Context(_click_app) as ctx:
            click.echo(_click_app.get_help(ctx))

        print_list(self.operators)
