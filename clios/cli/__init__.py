import typing as t

from .app import Clios, Input, OperatorFns

registry = OperatorFns()


@registry.register(name="print")
def output(input: t.Annotated[t.Any, Input()]) -> None:
    """
    Print the given input data to the terminal.

    description:
        It uses the `rich` library to print the data in a formatted way.
    """
    print(input)


main = Clios(registry)
