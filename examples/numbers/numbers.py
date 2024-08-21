# [start]
from clios import Clios

app = Clios()
# [app_created]


@app.reader()
def reader_int(input: str) -> int:
    return int(input)


@app.writer()
def writer_int(input: int):
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


# [main_start]
if __name__ == "__main__":
    import sys

    app.parse_args(sys.argv[1:]).execute()
# [main_end]
