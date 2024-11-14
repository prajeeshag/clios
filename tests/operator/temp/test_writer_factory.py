# type: ignore

import pytest

from clios.exceptions import InvalidFunction
from clios.operator import writer_factory

from .testdata.writer_invalid_fns import failing
from .testdata.writer_valid_fns import passing


@pytest.mark.parametrize("input", failing)
def test_failing(input):
    with pytest.raises(InvalidFunction) as e:
        writer_factory(input.fn)
    assert str(e.value) == str(input.e)
    assert e.value.fn == input.e.fn
    assert e.value.pname == input.e.pname


@pytest.mark.parametrize("input", passing)
def test_passing(input):
    op = writer_factory(input.fn)
    assert op == input
