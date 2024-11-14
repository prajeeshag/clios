# type: ignore
import pytest

from clios.operator import Writer


@pytest.mark.parametrize("params", [[1], [1, "s"], [1, "s", "z", "a"]])
def test_call(mocker, params):
    fn = mocker.Mock()
    fn.__name__ = "fn"
    operator = Writer(fn, int, 1)
    operator(*params)
    fn.assert_called_once_with(*params)
