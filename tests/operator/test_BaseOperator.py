# type: ignore
from dataclasses import dataclass

import pytest
from clio.operator import BaseOperator


@dataclass
class _P:
    name: str


def fn(): ...


def test_no_var_arg():
    op = BaseOperator(
        fn,
        int,
        (_P("1"), _P("2"), _P("3")),
        required_kwargs=(_P("r1"), _P("r2")),
        optional_kwargs=(_P("o1"),),
    )

    assert op.num_args == 3
    for n in range(3):
        assert op.get_arg(n) == _P(f"{n+1}")

    with pytest.raises(IndexError):
        op.get_arg(4)

    assert op.required_kwarg_keys == ("r1", "r2")
    assert op.optional_kwarg_keys == ("o1",)

    for k in ("r1", "r2", "o1"):
        assert op.get_kwarg(k) == _P(f"{k}")


def test_var_arg():
    op = BaseOperator(
        fn,
        int,
        (_P("1"), _P("2"), _P("3")),
        var_arg=_P("varg"),
        required_kwargs=(_P("r1"), _P("r2")),
        optional_kwargs=(_P("o1"),),
        var_kwarg=_P("vkwarg"),
    )

    assert op.num_args == 3
    for n in range(3):
        assert op.get_arg(n) == _P(f"{n+1}")

    for n in range(3, 6):
        assert op.get_arg(n) == _P("varg")

    assert op.required_kwarg_keys == ("r1", "r2")
    assert op.optional_kwarg_keys == ("o1",)

    for k in ("r1", "r2", "o1"):
        assert op.get_kwarg(k) == _P(f"{k}")

    for i in range(3):
        assert op.get_kwarg(f"{i}") == _P("vkwarg")
