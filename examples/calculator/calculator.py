# [start]
from clios import Clios

app = Clios()
# [app_created]


@app.operator()
def add(input1: float, input2: float) -> float:
    return input1 + input2


@app.operator()
def sub(input1: float, input2: float) -> float:
    return input1 - input2


@app.operator()
def sqrt(input: float) -> float:
    """Calculate the square root of a number."""
    return input**0.5


@app.operator()
def mean(*inputs: float) -> float:
    """Calculate the mean of a list of numbers."""
    return sum(inputs) / len(inputs)


# [main_start]
if __name__ == "__main__":
    app()
# [main_end]
