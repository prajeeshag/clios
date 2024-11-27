import sys
import typing as t

import click
from rich import print

from clios.core.param_parser import ParamParserAbc

from ..core.operator_fn import OperatorFn
from ..core.operator_fn import OperatorFns as OperatorFns_
from ..core.param_info import Input
from .main_parser import CliParser
from .param_parser import StandardParamParser
from .presenter import CliPresenter


def output(input: t.Annotated[t.Any, Input()]) -> None:
    """
    Print the given input data to the terminal.

    description:
        It uses the `rich` library to print the data in a formatted way.
    """
    print(input)


standard_param_parser = StandardParamParser()


class OperatorFns(OperatorFns_):
    @t.override
    def register(
        self,
        *,
        name: str = "",
        param_parser: ParamParserAbc = standard_param_parser,
        implicit: t.Literal["input", "param"] = "input",
    ) -> t.Callable[..., t.Any]:
        return super().register(name=name, param_parser=param_parser, implicit=implicit)


class Clios:
    def __init__(self, operator_fns: OperatorFns_) -> None:
        self._operators = OperatorFns_()
        self._operators["print"] = OperatorFn.validate(
            output, param_parser=standard_param_parser
        )
        self._operators.update(operator_fns)
        self._parser = CliParser()
        self._presenter = CliPresenter(self._operators, self._parser)

    def __call__(self):
        try:
            args, options = _click_app(standalone_mode=False)
        except click.exceptions.UsageError as e:
            print(e.format_message())
            sys.exit(1)

        if options["list"]:
            return self._presenter.print_list()
        if options["show"] is not None:
            return self._presenter.print_detail(options["show"])
        if options["dry_run"]:
            return self._presenter.dry_run(args)
        if args:
            return self._presenter.run(args)

        with click.Context(_click_app) as ctx:
            click.echo(_click_app.get_help(ctx))


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
def _click_app(ctx: t.Any, **kwargs: t.Any) -> tuple[list[str], dict[str, t.Any]]:
    return ctx.args, kwargs
