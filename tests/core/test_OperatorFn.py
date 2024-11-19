# type: ignore
import typing as t

import pytest
from typing_extensions import Doc

from clios.core.arg_parser import OprArgParserAbc
from clios.core.operator_fn import OperatorFn
from clios.core.param_info import Input, Output, Param
from clios.core.parameter import Parameters, ReturnValue


@pytest.fixture
def mock_arg_parser(mocker):
    return mocker.MagicMock(spec=OprArgParserAbc)


def fn(
    in1: int,
    in2: t.Annotated[str, Input()],
    p1: t.Annotated[str, Param(build_phase_validators=[int])],
    p2: t.Annotated[str, Param(strict=True)] = "default",
    *var_args: int,
    k1: t.Annotated[str, Param(), Doc("k1 doc")],
    k2: t.Annotated[str, Param()] = "default",
    **var_kwds: t.Annotated[int, Param()],
) -> t.Annotated[int, Output()]:
    """
    Short description

    Long description
    """
    pass


def test_(mock_arg_parser):
    op = OperatorFn.validate(fn, arg_parser=mock_arg_parser)
    op1 = OperatorFn.validate(fn, arg_parser=mock_arg_parser, implicit="param")
    assert isinstance(op, OperatorFn)
    assert isinstance(op.parameters, Parameters)
    assert op.callback is fn
    assert isinstance(op.output, ReturnValue)
    assert op.parameters[0].is_input
    assert op.parameters[0].type_ is int
    assert op.parameters[1].name == "in2"
    assert op.parameters[1].is_input
    assert op.parameters[1].type_ is str
    assert op.parameters[2].is_param
    assert op.parameters[2].is_positional_param
    assert not op.parameters[2].is_input
    assert op.parameters[3].default == "default"
    assert op.parameters[4].is_var_input
    assert op1.parameters[4].is_var_param
    assert op.parameters[6].is_keyword_param
    assert op.parameters[7].is_var_keyword
