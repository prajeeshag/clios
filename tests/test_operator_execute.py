# type: ignore
import sys
import typing as t

import pytest
from pydantic import ValidationError

from clios.cli.main_parser import CliParser
from clios.cli.param_parser import CliParamParser
from clios.core.operator import OperatorError, RootOperator
from clios.core.operator_fn import OperatorFn
from clios.core.param_info import Input, Output, Param
from clios.core.registry import OperatorRegistry

intOut = t.Annotated[int, Output(callback=print)]


intParam = t.Annotated[int, Param()]
intIn = t.Annotated[int, Input()]

IntParam = t.Annotated[int, Param(core_validation_phase="execute")]
IntIn = t.Annotated[int, Input(core_validation_phase="execute")]


def op_():
    pass


def op_1o_noroot() -> int:
    pass


def op_1i(i: intIn):
    pass


def op_1I(i: IntIn):
    pass


def op_2i(i: intIn, j: intIn):
    pass


def op_1o() -> intOut:
    return 1


def op_1oe() -> intOut:
    return "a"


def op_vi(*i: intIn):
    pass


def op_1k(*, ip: intParam):
    pass


def op_1p(ip: intParam):
    pass


def op_vp(*ip: intParam):
    pass


def op_1K(*, ip: IntParam):
    pass


def op_1P(ip: IntParam):
    pass


def op_1p1o(ip: intParam) -> intOut:
    return 1


def op_1i1k(i: intIn, *, ip: intParam):
    pass


def op_1i1p(i: intIn, ip: intParam):
    pass


def op_1i1o(i: intIn) -> intOut:
    return 1


def op_1i1oe(i: intIn) -> intOut:
    return "a"


def op_1i1p1o(i: intIn, ip: intParam) -> intOut:
    return 1


def op_1i1k1o(i: intIn, *, ip: intParam) -> intOut:
    return 1


def list_functions():
    current_module = sys.modules[__name__]
    ff_functions = [
        getattr(current_module, func)
        for func in dir(current_module)
        if func.startswith("op") and callable(getattr(current_module, func))
    ]
    return ff_functions


operators = OperatorRegistry()
for func in list_functions():
    operators.add(
        func.__name__, OperatorFn.validate(func, param_parser=CliParamParser())
    )


execute_error = [
    [
        ["-op_1P,a"],
        "Data validation failed for the argument `ip` of operator `op_1P`!",
    ],
    [
        ["-op_1K,ip=a"],
        "Data validation failed for the argument `ip` of operator `op_1K`!",
    ],
    [
        ["-op_1I", "input"],
        "Data validation failed for the input of operator `op_1I`!",
    ],
]


@pytest.mark.parametrize("input,expected", execute_error)
def test_error(input, expected):
    parser = CliParser()
    op = parser.get_operator(operator_fns=operators, input=input)
    with pytest.raises(OperatorError) as e:
        op.execute()
    assert e.value.message == expected
    assert isinstance(e.value.ctx["error"], ValidationError)
    assert str(e.value)


valid = [
    [["-op_"], "[ op_ ]"],
    [["-op_1i", "-op_1p1o,1"], "[ op_1i [ op_1p1o ] ]"],
    [
        ["-op_1i1o", "-op_1p1o,1", "output"],
        "output [ op_1i1o [ op_1p1o ] ]",
    ],
    [["-op_1i", "100"], "[ op_1i [ 100 ] ]"],
    [["-op_vi", "1", "1", "1", "1"], "[ op_vi [ 1 1 1 1 ] ]"],
    [["-op_vp,1,1,1,1,1"], "[ op_vp ]"],
    [["-op_1i1p,1", "1"], "[ op_1i1p [ 1 ] ]"],
]


@pytest.mark.parametrize("input,expected_draw", valid)
def test_draw(input, expected_draw):
    parser = CliParser()
    op = parser.get_operator(operator_fns=operators, input=input)
    assert isinstance(op, RootOperator)
    assert op.draw() == expected_draw
    op.execute()


def test_output_validation_failed():
    parser = CliParser()
    op = parser.get_operator(operator_fns=operators, input=["-op_1oe", "output"])
    op1 = parser.get_operator(
        operator_fns=operators, input=["-op_1i1oe", "-op_1o", "output"]
    )
    with pytest.raises(OperatorError) as e:
        op.execute()

    assert "Data validation failed for the output of operator `op_1oe`!" in str(e.value)
    assert "It's a bug! Please report it!" in str(e.value)

    with pytest.raises(OperatorError):
        op1.execute()
