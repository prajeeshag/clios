from typing import Annotated, Any

from clios import OperatorFns, Output, Param

operators = OperatorFns()


@operators.register(name="print", implicit="input")
def print_(input: Any) -> None:
    """Print the given input data to the terminal."""
    print(input)


@operators.register(implicit="input")
def add(input1: float, input2: float) -> float:
    """Add two numbers."""
    return input1 + input2


@operators.register(implicit="input")
def sub(input1: float, input2: float) -> float:
    """Subtract two numbers."""
    return input1 - input2


@operators.register(implicit="input")
def mul(input1: float, input2: float) -> float:
    """Multiply two numbers."""
    return input1 * input2


@operators.register(implicit="input")
def div(input1: float, input2: float) -> float:
    """Divide two numbers."""
    return input1 / input2


@operators.register(implicit="input")
def sqrt(input: float) -> float:
    """Calculate the square root of a number."""
    return input**0.5


@operators.register(implicit="input")
def mean(*inputs: float) -> float:
    """Calculate the mean of a list of numbers."""
    return sum(inputs) / len(inputs)


floatParam = Annotated[float, Param()]


def file_writer(content: Any, file_path: str) -> None:
    import json

    with open(file_path, "w") as f:
        f.write(json.dumps(content))


floatOutput = Annotated[list[float], Output(callback=file_writer)]


@operators.register(name="range", implicit="param")
def range_(start: floatParam, end: floatParam, step: floatParam = 1) -> floatOutput:
    """Generate a range of numbers."""
    return list(range(int(start), int(end), int(step)))


if __name__ == "__main__":
    from clios import Clios

    app = Clios(operators)
    app()
