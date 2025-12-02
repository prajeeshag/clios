import typing as t

import click
from rich import print

from clios.core.param_parser import ParamParserAbc

from ..core.operator_fn import OperatorFn
from ..core.operator_fn import OperatorFns as OperatorFns_
from .main_parser import CliParser
from .param_parser import StandardParamParser
from .presenter import CliPresenter

standard_param_parser = StandardParamParser()


def operator(
    *,
    param_parser: ParamParserAbc = standard_param_parser,
    implicit: t.Literal["input", "param"] = "param",
) -> t.Callable[..., t.Any]:
    def decorator(func: t.Callable[..., t.Any]) -> OperatorFn:
        operator_fn = OperatorFn.from_def(
            func, param_parser=param_parser, implicit=implicit
        )
        return operator_fn

    return decorator


class OperatorFns(OperatorFns_):
    @t.override
    def register(
        self,
        *,
        name: str = "",
        param_parser: ParamParserAbc = standard_param_parser,
        implicit: t.Literal["input", "param"] = "param",
        is_delegate: bool = False,
    ) -> t.Callable[..., t.Any]:
        return super().register(
            name=name,
            param_parser=param_parser,
            implicit=implicit,
            is_delegate=is_delegate,
        )


class Clios:
    def __init__(self, operator_fns: OperatorFns_, exe_name: str = "") -> None:
        self._operators = operator_fns
        self._parser = CliParser()
        self._presenter = CliPresenter(self._operators, self._parser)
        self._exe_name = exe_name

    def __call__(self):
        try:
            res = _click_app(standalone_mode=False)
        except click.exceptions.UsageError as e:
            print(e.format_message())
            with click.Context(_click_app) as ctx:
                click.echo(_click_app.get_help(ctx))
            raise SystemExit(1)

        if isinstance(res, tuple):
            args, options = res
        elif res != 0:
            raise SystemExit(res)
        else:
            return

        if options["list"]:
            return self._presenter.print_list()
        if options["show"] is not None:
            return self._presenter.print_detail(options["show"], self._exe_name)
        if options["dry_run"]:
            return self._presenter.dry_run(args)
        debug = options["debug"]
        return self._presenter.run(args, debug)


@click.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
@click.option("--list", type=bool, help="List all available operators", is_flag=True)
@click.option("--debug", type=bool, help="Turn on debugging", is_flag=True)
@click.option(
    "--show", type=str, help="Show the help information for the given operator", nargs=1
)
@click.option(
    "--dry-run", type=bool, help="Dry run: prints the call tree", is_flag=True
)
@click.pass_context
def _click_app(ctx: t.Any, **kwargs: t.Any) -> tuple[list[str], dict[str, t.Any]]:
    return ctx.args, kwargs
