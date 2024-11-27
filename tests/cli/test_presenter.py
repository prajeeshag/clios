# type: ignore
import typing as t

import pytest
from typing_extensions import Doc

from clios.cli.main_parser import CliParser
from clios.cli.param_parser import StandardParamParser
from clios.cli.presenter import CliPresenter
from clios.core.main_parser import ParserError
from clios.core.operator_fn import OperatorFn, OperatorFns
from clios.core.param_info import Param


@pytest.fixture
def mock_console(mocker):
    return mocker.patch("clios.cli.presenter.Console")


@pytest.fixture
def mock_panel(mocker):
    return mocker.patch("clios.cli.presenter.Panel")


@pytest.fixture
def mock_table(mocker):
    return mocker.patch("clios.cli.presenter.Table")


@pytest.fixture
def mock_text(mocker):
    return mocker.patch("clios.cli.presenter.Text")


def operator1(
    input1: int,
    input2: int,
    param1: t.Annotated[int, Param(), Doc("Parameter 1")],
    *,
    param2: t.Annotated[int, Param(), Doc("Parameter 2")] = 10,
) -> int:
    """
    Operator 1

    description:
        Long description of operator 1

    Operator Examples:
        operator1 input output
        operator1 input output
    """
    return 1


@pytest.fixture
def get_presenter(mocker):
    param_parser = StandardParamParser()

    def _presenter(fns):
        operator_fns = OperatorFns()
        for fn in fns:
            operator_fns[fn.__name__] = OperatorFn.validate(
                fn, param_parser=param_parser
            )
        return CliPresenter(operator_fns=operator_fns, parser=CliParser())

    return _presenter


def test_print_list(get_presenter, mock_console, mock_table, mocker):
    presenter = get_presenter([operator1])
    presenter.print_list()
    mock_console().print.assert_called()
    mock_table.assert_called_with(
        show_header=True, header_style="bold blue", title="Available Operators"
    )
    mock_table().add_column.assert_has_calls(
        [
            mocker.call("Operator", no_wrap=True, min_width=9, style="bold"),
            mocker.call("Description"),
        ]
    )
    mock_table().add_row.assert_called_with("operator1", "Operator 1")


def test_print_detail(
    get_presenter,
    mock_console,
    mock_panel,
    mock_table,
    mock_text,
    mocker,
):
    presenter = get_presenter([operator1])

    synopsis = mocker.MagicMock()
    description_text = mocker.MagicMock()
    description_panel = mocker.MagicMock()
    positionals = mocker.MagicMock()
    keywords = mocker.MagicMock()
    examples_text = mocker.MagicMock()
    examples = mocker.MagicMock()

    mock_text.side_effect = [description_text, examples_text]
    mock_panel.side_effect = [synopsis, description_panel, examples]
    mock_table.side_effect = [positionals, keywords]

    presenter.print_detail("operator1")

    description_text.append.assert_has_calls(
        [
            mocker.call("Operator 1\n\n", style="bold blue"),
            mocker.call("Long description of operator 1", style="dim"),
        ]
    )

    examples_text.append.assert_called_with(
        "operator1 input output\noperator1 input output", style="italic"
    )

    mock_panel.assert_has_calls(
        [
            mocker.call(
                "operator1,param1[,param2=<val>] input1 input2 output",
                title="Synopsis",
                style="bold yellow",
                title_align="left",
                padding=(1, 2),
            ),
            mocker.call(
                description_text,
                title="Description",
                style="bold blue",
                title_align="left",
                padding=(1, 2),
            ),
            mocker.call(
                examples_text,
                title="Examples",
                style="bold magenta",
                title_align="left",
                padding=(1, 2),
            ),
        ]
    )

    mock_table.assert_has_calls(
        [
            mocker.call(
                title="Positional Arguments",
                show_header=True,
                header_style="bold magenta",
            ),
            mocker.call(
                title="Keyword Arguments",
                show_header=True,
                header_style="bold magenta",
            ),
        ]
    )
    positionals.add_column.assert_has_calls(
        [
            mocker.call("Parameter", style="dim", no_wrap=True),
            mocker.call("Type", style="dim", no_wrap=True),
            mocker.call("Required", style="dim", no_wrap=True),
            mocker.call("Description", justify="left"),
        ]
    )
    positionals.add_row.assert_has_calls(
        [
            mocker.call("param1", "INT", "Required", "Parameter 1"),
        ]
    )

    keywords.add_column.assert_has_calls(
        [
            mocker.call("Parameter", style="dim", no_wrap=True),
            mocker.call("Type", style="dim", no_wrap=True),
            mocker.call("Required", style="dim", no_wrap=True),
            mocker.call("Description", justify="left"),
        ]
    )
    keywords.add_row.assert_has_calls(
        [
            mocker.call("param2", "INT", "Optional", "Parameter 2 (default: 10)"),
        ]
    )

    mock_console().print.assert_has_calls(
        [
            mocker.call(synopsis),
            mocker.call(description_panel),
            mocker.call(positionals),
            mocker.call(keywords),
            mocker.call(examples),
        ]
    )


def test_print_details_empty(get_presenter, mock_console, mock_panel, mock_text):
    def output(i: int) -> int:
        pass

    get_presenter([output]).print_detail("output")


def test_process_error(get_presenter, mock_console, mock_panel, mock_text):
    error = ParserError("Test error", ctx={"token_index": 2})
    args = ["arg1", "arg2", "arg3", "arg4", "arg5"]
    get_presenter([operator1]).process_error(error, args)
    mock_console().print.assert_called()
    mock_text.assert_called_with("Test error", style="bold red")


def test_process_error_no_ctx(get_presenter, mock_console, mock_panel, mock_text):
    error = ParserError("Test error")
    args = ["arg1", "arg2", "arg3", "arg4", "arg5"]
    get_presenter([operator1]).process_error(error, args)
    mock_console().print.assert_called()
    mock_text.assert_called_with("Test error", style="bold red")


def test_print_details_operator_not_found(get_presenter):
    with pytest.raises(SystemExit):
        get_presenter([operator1]).print_detail("operator2")


def test_dry_run_fail(get_presenter):
    presenter = get_presenter([operator1])
    with pytest.raises(SystemExit):
        presenter.dry_run(["operator1,1", "1", "output"])


def test_dry_pass(get_presenter):
    def output(i: t.Any):
        pass

    presenter = get_presenter([operator1, output])
    presenter.dry_run(["output", "-operator1,1", "1", "2"])


def test_run_fail(get_presenter):
    def output(i: t.Any):
        pass

    def op1() -> int:
        return "1"

    presenter = get_presenter([operator1, output, op1])
    with pytest.raises(SystemExit):
        presenter.run(["operator1,1", "1", "output"])

    with pytest.raises(SystemExit):
        presenter.run(["output", "-op1"])

    presenter.run(["output", "-operator1,1", "1", "2"])
