import typing as t

from rich import print

from .cli.app import Clios as Clios
from .cli.app import OperatorFns as OperatorFns
from .cli.app import operator as operator
from .core.exceptions import CliosError as CliosError
from .core.operator import OperatorError as OperatorError
from .core.param_info import Input as Input
from .core.param_info import Output as Output
from .core.param_info import Param as Param

registry = OperatorFns()


@registry.register(name="print")
def _output(input: t.Annotated[t.Any, Input()]) -> None:
    """
    Print the given input data to the terminal.

    description:
        It uses the `rich` library to print the data in a formatted way.
    """
    print(input)  # noqa: T201 # pragma: no cover


main = Clios(registry)
