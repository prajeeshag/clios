# type: ignore
import inspect
from typing import Annotated

import pytest

from clios.exceptions import InvalidArguments as Error
from clios.operator import operator_factory

from .testdata.operator_valid_fns import _toBoolReader

_nil = inspect.Parameter.empty


@pytest.mark.parametrize(
    "params,kwds,res",
    [
        [
            [("*i", int, _nil)],
            dict(j=1),
            Error("Got an unexpected keyword argument [j]"),
        ],
        [
            [("*i", int, _nil), ("j", int, _nil)],
            dict(),
            Error("Missing required keyword argument [j]"),
        ],
    ],
)
def test_load_kwargs_wrong_inputs(mocker, params, kwds, res):
    op = arrange(mocker, params)
    with pytest.raises(Error) as e:
        op.load_kwargs(kwds)
    assert str(e.value) == str(res)


@pytest.mark.parametrize(
    "params,args,res",
    [
        [[], [10, 20], Error("Expected 0 argument(s), got 2")],
        [[("i", int, _nil)], [], Error("Expected 1 argument(s), got 0")],
        [[("i", int, _nil)], [10, 20], Error("Expected 1 argument(s), got 2")],
    ],
)
def test_load_args_wrong_inputs(mocker, params, args, res):
    op = arrange(mocker, params)
    with pytest.raises(Error) as e:
        op.load_args(args)
    assert str(e.value) == str(res)


@pytest.mark.parametrize(
    "params,args,res",
    [
        [[("*i", int, _nil)], ["1", "2"], (1, 2)],
        [[("i", int, _nil), ("j", float, _nil)], ["1", "2"], (1, 2.0)],
        [[("*i", int, _nil), ("j", float, _nil)], [], ()],
        [[("**i", int, _nil)], [], ()],
        [
            [("*j", str, _nil), ("**i", int, _nil)],
            ["abcd", "1234"],
            ("abcd", "1234"),
        ],
        [[("input", int, _nil), ("**i", int, _nil)], [], ()],
        [
            [("*i", Annotated[bool, _toBoolReader], _nil)],
            ["1", "0"],
            (True, False),
        ],
    ],
)
def test_load_args_valid_inputs(mocker, params, args, res):
    op = arrange(mocker, params)
    result = op.load_args(args)
    assert result == res


@pytest.mark.parametrize(
    "params,kwds,res",
    [
        [[("*i", int, _nil)], dict(), {}],
        [[("i", int, _nil), ("j", float, _nil)], dict(), {}],
        [[("*i", int, _nil), ("j", float, _nil)], dict(j="2"), {"j": 2.0}],
        [[("**i", int, _nil)], dict(j="2"), {"j": 2}],
        [
            [("*j", str, _nil), ("**i", int, _nil)],
            dict(j="2"),
            {"j": 2},
        ],
        [[("input", int, _nil), ("**i", int, _nil)], dict(j="2"), {"j": 2}],
    ],
)
def test_load_kwargs_valid_inputs(mocker, params, kwds, res):
    op = arrange(mocker, params)
    result = op.load_kwargs(kwds)
    assert result == res


def arrange(mocker, params):
    fn = mocker.Mock()
    inspect_function = mocker.patch("clios.operator._Operator.inspect_function")
    inspect_function.return_value = ("name", params, int)
    op = operator_factory(fn)
    return op
