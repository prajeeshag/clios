import sys
from typing import Annotated, Any, Callable, Literal

import click
from rich import print

from ..core.operator_fn import OperatorFn
from ..core.param_info import Input
from ..core.registry import OperatorRegistry
from .main_parser import CliParser
from .param_parser import CliParamParser
from .presenter import CliPresenter


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
@click.option(
    "--dry-run", type=bool, help="Dry run: prints the call tree", is_flag=True
)
@click.pass_context
def _click_app(ctx: Any, **kwargs: Any) -> tuple[list[str], dict[str, Any]]:
    return ctx.args, kwargs


default_param_parser = CliParamParser()


class Clios:
    def __init__(self) -> None:
        self.operators = OperatorRegistry()
        self.parser = CliParser()
        self.operators.add(
            "print",
            OperatorFn.validate(
                output,
                param_parser=default_param_parser,
            ),
        )
        self.presenter = CliPresenter(self.operators, self.parser)

    def operator(
        self,
        name: str = "",
        param_parser: CliParamParser = default_param_parser,
        implicit: Literal["input", "param"] = "input",
    ) -> Any:
        def decorator(func: Callable[..., Any]):
            op_obj = OperatorFn.validate(
                func,
                param_parser=param_parser,
                implicit=implicit,
            )
            key = name if name else func.__name__
            self.operators.add(key, op_obj)
            return func

        return decorator

    def __call__(self):
        try:
            args, options = _click_app(standalone_mode=False)
        except click.exceptions.UsageError as e:
            print(e.format_message())
            sys.exit(1)

        if options["list"]:
            return self.presenter.print_list()
        if options["show"] is not None:
            return self.presenter.print_detail(options["show"])
        if options["dry_run"]:
            return self.presenter.dry_run(args)
        if args:
            return self.presenter.run(args)

        with click.Context(_click_app) as ctx:
            click.echo(_click_app.get_help(ctx))
        # self.presenter.print_list()
