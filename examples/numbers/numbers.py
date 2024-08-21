import sys

from clios import Clios

app = Clios()


@app.reader()
def reader_int(input: str) -> int:
    return int(input)


@app.writer()
def writer_int(input: int):
    print(input)


@app.writer()
def writer_float(input: float):
    print(input)


@app.operator()
def add(input: tuple[int, int]) -> int:
    return input[0] + input[1]


@app.operator()
def sub(input: tuple[int, int]) -> int:
    return input[0] - input[1]


@app.operator(name="sum")
def sum_int(input: tuple[int, ...]) -> int:
    return sum(input)


if __name__ == "__main__":
    app.parse_args(sys.argv[1:]).execute()
