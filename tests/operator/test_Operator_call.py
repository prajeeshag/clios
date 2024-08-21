# type: ignore
import inspect

import pytest
from clio.operator import Operator
from clio.operator._Operator import _Input

_nil = inspect.Parameter.empty


@pytest.mark.parametrize(
    "dtype, input, fn_input, var_tuple, var_list",
    [
        [(int,), (1,), 1, False, False],
        [(int,), (1,), [1], False, True],
        [(int,), (1,), (1,), True, False],
        [(int, int), (1, 2), (1, 2), False, False],
        [(int,), (1, 2), [1, 2], False, True],
        [(int,), (1, 2), (1, 2), True, False],
    ],
)
@pytest.mark.parametrize(
    "args,kwds,res",
    [
        [["s"], {"k": 1}, 1],
        [[], {"k": 1}, "s"],
        [["s"], {}, True],
        [["s", "i"], {}, 10.5],
        [[], {"k": 1, "f": "s"}, None],
    ],
)
def test_call(mocker, dtype, input, fn_input, var_tuple, var_list, args, kwds, res):
    fn = mocker.Mock()
    fn.return_value = res
    fn.__name__ = "fn"
    operator = Operator(
        fn,
        output_type=type(res),
        input=_Input(dtype, var_list=var_list, var_tuple=var_tuple),
    )
    result = operator(input, *args, **kwds)
    fn.assert_called_once_with(fn_input, *args, **kwds)
    assert result == res


def test_typeerror(mocker):
    fn = mocker.Mock()
    fn.return_value = 1
    fn.__name__ = "name"
    operator = Operator(fn, output_type=str, input=_Input((int,)))
    with pytest.raises(TypeError) as e:
        operator((1,))
    assert str(e.value) == "Expected <str> but received <int> from function <name>"
