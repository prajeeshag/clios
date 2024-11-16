# [start]
from clios import Clios

app = Clios()
# [app_created]


@app.operator()
def add(input1: int, input2: int) -> int:
    return input1 + input2


@app.operator()
def sub(input1: int, input2: int) -> int:
    return input1 - input2


@app.operator(name="sum")
def sum_(*input: int) -> int:
    return sum(input)


# [main_start]
if __name__ == "__main__":
    app()
# [main_end]
