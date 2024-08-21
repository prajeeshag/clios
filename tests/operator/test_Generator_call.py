# type: ignore
import inspect

import pytest
from clio.operator import Generator

_nil = inspect.Parameter.empty


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
def test_call(mocker, args, kwds, res):
    fn = mocker.Mock()
    fn.return_value = res
    fn.__name__ = "fn"
    operator = Generator(fn, output_type=type(res))
    result = operator(*args, **kwds)
    fn.assert_called_once_with(*args, **kwds)
    assert result == res


def test_typeerror(mocker):
    fn = mocker.Mock()
    fn.return_value = 1
    fn.__name__ = "name"
    operator = Generator(fn, output_type=str)
    with pytest.raises(TypeError) as e:
        operator()
    assert str(e.value) == "Expected <str> but received <int> from function <name>"
