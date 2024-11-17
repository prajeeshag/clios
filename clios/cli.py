from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .exceptions import CliosError
from .operator.model import OperatorFn
from .registry import OperatorRegistry


def process_error(error: CliosError) -> None:
    pass


def print_list(operators: OperatorRegistry):
    """
    Prints a 2-column table dynamically adjusted to the terminal width.

    Args:
        data (list[tuple[str, str]]): A list of tuples containing data for the table.
    """
    console = Console()
    table = Table(
        show_header=True, header_style="bold blue", title="Available Operators"
    )
    data = [(name, op.short_description) for name, op in operators.items()]
    # Add columns with dynamic width for the second column
    column1_width = max(len(row[0]) for row in data)
    column1_width = max(len("Operator"), column1_width)
    table.add_column("Operator", no_wrap=True, min_width=column1_width, style="bold")
    # table.add_column("Description", width=console.size.width - column1_width - 10)
    table.add_column("Description")
    # Add rows
    for col1, col2 in data:
        table.add_row(col1, col2)
    console.print(table)


def print_detail(name: str, op: OperatorFn) -> None:
    """
    Prints a detailed operator page using Rich.
    """
    console = Console()

    synopsis = op.get_synopsis(name)
    short_description = op.short_description
    long_description = op.long_description
    args_doc = op.get_args_doc()
    kwds_doc = op.get_kwds_doc()

    # Synopsis
    synopsis_panel = Panel(
        synopsis,
        title="Synopsis",
        style="bold yellow",
    )

    # Render all parts
    console.print(synopsis_panel)
    if long_description or short_description:
        description_text = Text()
        description_text.append(f"{short_description}\n\n", style="bold blue")
        if long_description:
            description_text.append(long_description, style="dim")
        description_panel = Panel(
            description_text,
            title="Description",
            style="bold blue",
        )
        console.print(description_panel)

    if args_doc:
        param_table_args = create_param_table(args_doc, title="Positional Arguments")
        console.print(param_table_args)

    if kwds_doc:
        param_table_kwds = create_param_table(kwds_doc, title="Keyword Arguments")
        console.print(param_table_kwds)


def create_param_table(args_doc: Any, title: str) -> Table:
    param_table = Table(title=title, show_header=True, header_style="bold magenta")
    param_table.add_column("Parameter", style="dim", no_wrap=True)
    param_table.add_column("Type", style="dim", no_wrap=True)
    param_table.add_column("Required", style="dim", no_wrap=True)
    param_table.add_column("Description", justify="left")
    for doc in args_doc:
        required = "Required" if doc.default == "" else "Optional"
        description = doc.description
        if doc.default != "":
            description += f" (default: {doc.default})"
        param_table.add_row(doc.repr, doc.type_, required, description)
    return param_table
