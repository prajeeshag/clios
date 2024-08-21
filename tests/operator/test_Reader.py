# type: ignore

import pytest
from clio.operator import Reader, reader_factory


def test_call(mocker):
    fn = mocker.Mock()
    fn.return_value = 1
    fn.__name__ = "fn"
    operator = Reader(fn, int)
    result = operator("s")
    fn.assert_called_once_with("s")
    assert result == 1


def fn02(i: str) -> str:
    return 1


def fn03(i: str) -> float:
    return "s"


@pytest.mark.parametrize(
    "fn,res",
    [
        [
            fn02,
            TypeError("Expected <str> but received <int> from function", fn02),
        ],
        [
            fn03,
            TypeError("Expected <float> but received <str> from function", fn03),
        ],
    ],
)
def test_typeerror(fn, res):
    operator = reader_factory(fn)
    with pytest.raises(TypeError) as e:
        operator("s")
    assert str(e.value) == str(res)
