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


@app.operator()
def fibo(n: int) -> tuple[int, ...]:
    a, b = 0, 1
    fib: list[int] = []
    for _ in range(n):
        fib.append(a)
        a, b = b, a + b
    return tuple(fib)


# [main_start]
if __name__ == "__main__":
    app()
# [main_end]
