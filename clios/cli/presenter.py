import enum
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from clios.core.main_parser import ParserAbc, ParserError
from clios.core.operator import OperatorError
from clios.core.operator_fn import OperatorFns


class _KnownTypes(enum.Enum):
    INT = int
    FLOAT = float
    TEXT = str
    BOOL = bool
    DATETIME = datetime
    DATE = date
    TIME = time
    TIMDELTA = timedelta

    @classmethod
    def _missing_(cls, value: Any) -> Any:
        return cls.TEXT


@dataclass(frozen=True)
class CliPresenter:
    operator_fns: OperatorFns
    parser: ParserAbc

    def process_error(self, error: ParserError, args: list[str]) -> None:
        """
        Process an error and present it nicely to the terminal.
        """
        # Get the error message
        message = error.message

        console = Console()

        # From context, get token_index if available
        token_index = error.ctx.get("token_index", None)
        unchainable_token_index = error.ctx.get("unchainable_token_index", None)
        error.ctx.get("num_extra_tokens", None)
        sub_error = error.ctx.get("error", None)

        if sub_error is not None:
            message += f"\n{str(sub_error)}"

        error_argument_text = Text()
        if token_index is not None:
            token_before = token_index - 1
            token_after = token_index + 1

            if token_before > 0:
                error_argument_text.append(" ")
                error_argument_text.append("...", style="dim")

            if token_before >= 0:
                error_argument_text.append(" ")
                error_argument_text.append(args[token_before], style="dim")

            error_argument_text.append(" ")
            error_argument_text.append(args[token_index], style="bold red underline")

            if token_after < len(args) and unchainable_token_index is None:
                error_argument_text.append(" ")
                error_argument_text.append(args[token_after], style="dim")

            if token_after < len(args) - 1:
                error_argument_text.append(" ")
                error_argument_text.append("...", style="dim")

            if unchainable_token_index is not None:
                error_argument_text.append(" ")
                error_argument_text.append(
                    args[unchainable_token_index], style="bold red underline"
                )

                if unchainable_token_index < len(args) - 1:
                    error_argument_text.append(" ")
                    error_argument_text.append("...", style="dim")

            console.print()
            console.print(error_argument_text)

        console.print()
        console.print(Text(message, style="bold red"))

    def print_list(self):
        """
        Prints a 2-column table dynamically adjusted to the terminal width.

        Args:
            data (list[tuple[str, str]]): A list of tuples containing data for the table.
        """
        console = Console()
        table = Table(
            show_header=True, header_style="bold blue", title="Available Operators"
        )
        data = [(name, op.short_description) for name, op in self.operator_fns.items()]
        # Add columns with dynamic width for the second column
        column1_width = max(len(row[0]) for row in data)
        column1_width = max(len("Operator"), column1_width)
        table.add_column(
            "Operator", no_wrap=True, min_width=column1_width, style="bold"
        )
        # table.add_column("Description", width=console.size.width - column1_width - 10)
        table.add_column("Description")
        # Add rows
        for col1, col2 in data:
            table.add_row(col1, col2)
        console.print()
        console.print(table)

    def print_detail(self, name: str):
        """
        Prints a detailed operator page using Rich.
        """
        console = Console()
        try:
            op_fn = self.operator_fns[name]
        except KeyError:
            print(f"Operator `{name}` not found!")
            raise SystemExit(1)

        synopsis = self.parser.get_synopsis(op_fn, name)

        short_description = op_fn.short_description
        long_description = op_fn.long_description
        args_doc: list[dict[str, str]] = []
        kwds_doc: list[dict[str, str]] = []
        for param in op_fn.parameters:
            if param.is_positional_param or param.is_var_param:
                docs = args_doc
            elif param.is_keyword_param or param.is_var_keyword:
                docs = kwds_doc
            else:
                continue
            doc: dict[str, Any] = {}
            doc["name"] = param.name
            doc["type"] = _KnownTypes(param.type_).name
            doc["required"] = "Required" if param.is_required else "Optional"
            doc["default_value"] = str(param.default)
            if param.default == "":
                doc["default_value"] = "''"
            if param.default is param.empty:
                doc["default_value"] = ""
            doc["description"] = param.description
            docs.append(doc)

        # Synopsis
        synopsis_panel = Panel(
            synopsis,
            title="Synopsis",
            style="bold yellow",
            title_align="left",
            padding=(1, 2),
        )

        # Render all parts
        console.print(synopsis_panel)
        description_text = Text()
        if short_description:
            description_text.append(f"{short_description}\n\n", style="bold blue")
        if long_description:
            description_text.append(long_description, style="dim")
        if short_description or long_description:
            description_panel = Panel(
                description_text,
                title="Description",
                style="bold blue",
                title_align="left",
                padding=(1, 2),
            )
            console.print(description_panel)

        if args_doc:
            param_table_args = _create_param_table(
                args_doc, title="Positional Arguments"
            )
            console.print(param_table_args)

        if kwds_doc:
            param_table_kwds = _create_param_table(kwds_doc, title="Keyword Arguments")
            console.print(param_table_kwds)

        examples: list[str] = []
        for _, example in op_fn.examples:
            examples.append(example)

        if examples:
            text = "\n".join(examples)
            examples_text = Text()
            examples_text.append(text, style="italic")
            examples_panel = Panel(
                examples_text,
                title="Examples",
                style="bold magenta",
                title_align="left",
                padding=(1, 2),
            )
            console.print(examples_panel)

    def dry_run(self, args: list[str]):
        """
        Dry run the operator function with the given arguments.
        """
        console = Console()
        try:
            operator = self.parser.get_operator(self.operator_fns, args)
        except ParserError as e:
            self.process_error(e, args)
            raise SystemExit(1)
        console.print(operator.draw())

    def run(self, args: list[str]):
        """
        Run the operator function with the given arguments.
        """
        try:
            operator = self.parser.get_operator(self.operator_fns, args)
        except ParserError as e:
            self.process_error(e, args)
            raise SystemExit(1)

        try:
            operator.execute()
        except OperatorError as e:
            Console().print(Text(str(e), style="bold red"))
            raise SystemExit(1)


def _create_param_table(args_doc: list[dict[str, str]], title: str) -> Table:
    param_table = Table(title=title, show_header=True, header_style="bold magenta")
    param_table.add_column("Parameter", style="dim", no_wrap=True)
    param_table.add_column("Type", style="dim", no_wrap=True)
    param_table.add_column("Required", style="dim", no_wrap=True)
    param_table.add_column("Description", justify="left")
    for doc in args_doc:
        description = doc["description"]
        default_value = doc["default_value"]
        if default_value != "":
            description += f" (default: {default_value})"
        param_table.add_row(
            doc["name"],
            doc["type"],
            doc["required"],
            description,
        )
    return param_table
