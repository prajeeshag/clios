# [start]
from typing import Annotated, Any

from clios import Clios, Param
from clios.operator.params import Output

app = Clios()
# [app_created]


@app.operator()
def add(input1: float, input2: float) -> float:
    return input1 + input2


@app.operator()
def sub(input1: float, input2: float) -> float:
    return input1 - input2


@app.operator()
def mul(input1: float, input2: float) -> float:
    return input1 * input2


@app.operator()
def div(input1: float, input2: float) -> float:
    return input1 / input2


@app.operator()
def sqrt(input: float) -> float:
    """Calculate the square root of a number."""
    return input**0.5


@app.operator()
def mean(*inputs: float) -> float:
    """Calculate the mean of a list of numbers."""
    return sum(inputs) / len(inputs)


floatParam = Annotated[float, Param()]


def file_writer(content: Any, file_path: str) -> None:
    import json

    with open(file_path, "w") as f:
        f.write(json.dumps(content))


floatOutput = Annotated[list[float], Output(file_saver=file_writer)]


@app.operator(name="range", implicit="param")
def range_(start: floatParam, end: floatParam, step: floatParam = 1) -> floatOutput:
    """Generate a range of numbers."""
    return list(range(int(start), int(end), int(step)))


# [main_start]
if __name__ == "__main__":
    app()
# [main_end]
