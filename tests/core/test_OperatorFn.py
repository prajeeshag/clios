# type: ignore
import typing as t

import pytest
from pydantic import BaseModel, TypeAdapter
from typing_extensions import Doc

from clios.core.operator_fn import OperatorFn
from clios.core.param_info import Input, Output, Param
from clios.core.param_parser import ParamParserAbc
from clios.core.parameter import Parameter, ParameterKind, Parameters, ReturnValue

from .testdata.operator_invalid_fns import failing, failing_parameter_validation


@pytest.fixture
def mock_arg_parser(mocker):
    return mocker.MagicMock(spec=ParamParserAbc)


@pytest.mark.parametrize("input", failing)
def test_failing(input, mock_arg_parser):
    with pytest.raises(AssertionError) as e:
        OperatorFn.from_def(input.fn, param_parser=mock_arg_parser, implicit="input")
    assert str(e.value) == str(input.e)


@pytest.mark.parametrize("input", failing_parameter_validation)
def test_failing_parameter_validation(input, mock_arg_parser):
    with pytest.raises(AssertionError) as e:
        OperatorFn.from_def(input.fn, param_parser=mock_arg_parser, implicit="input")
    assert str(e.value) == str(input.e)


def test_implicit_invalid(mock_arg_parser):
    def dummy(i: int):
        pass

    with pytest.raises(AssertionError) as e:
        OperatorFn.from_def(dummy, implicit="invalid", param_parser=mock_arg_parser)

    assert str(e.value) == "Invalid implicit option `invalid`"


class PydanticType(BaseModel):
    val: int


class SomeType:
    pass


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

    description:
        Long description

    Operator Examples:
        Example 1:
            $ cdo -fn,1 input output
            $ cdo -fn,1 input output

        Example 2:
            $ cdo -fn,2 input output
    """
    pass


def fn12():
    """
    Examples:
        Short description
    """


def fn_simple_example():
    """
    Operator Examples:
        $ cdo -fn,1 input output
        $ cdo -fn,2 input output
    """


def fn1() -> int:
    pass


def fn2(**var_kwd: t.Annotated[int, Param()]) -> int:
    pass


def fn3():
    pass


def fn4(in1: "PydanticType") -> int:
    pass


def fn5(in1: t.Annotated[SomeType, "someAnnotation"]) -> int:
    pass


def test_(mock_arg_parser):
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    op1 = OperatorFn.from_def(fn1, param_parser=mock_arg_parser, implicit="input")
    op12 = OperatorFn.from_def(fn12, param_parser=mock_arg_parser, implicit="input")
    op_simple_example = OperatorFn.from_def(
        fn_simple_example, param_parser=mock_arg_parser, implicit="input"
    )
    assert isinstance(op, OperatorFn)
    assert isinstance(op.parameters, Parameters)
    assert isinstance(op.output, ReturnValue)
    assert op.callback is fn
    assert op.param_parser is mock_arg_parser
    assert op.short_description == "Short description"
    assert op.long_description == "Long description"
    assert op.examples[0][0] == "Example 1"
    assert op.examples[0][1] == "$ cdo -fn,1 input output\n$ cdo -fn,1 input output"
    assert op.examples[1][0] == "Example 2"
    assert op.examples[1][1] == "$ cdo -fn,2 input output"
    assert op1.short_description == ""
    assert op1.long_description == ""
    assert op1.examples == []
    assert op12.examples == []
    assert op12.long_description == ""
    assert op12.short_description == ""
    assert op_simple_example.examples[0][0] == ""
    assert (
        op_simple_example.examples[0][1]
        == "$ cdo -fn,1 input output\n$ cdo -fn,2 input output"
    )


def test_Parameter_is_input():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    op1 = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="param")
    assert op.parameters[0].is_input
    assert op.parameters[1].is_input
    assert op.parameters[2].is_input is False
    assert op.parameters[3].is_input is False
    assert op.parameters[4].is_input
    assert op1.parameters[4].is_input is False


def test_Parameter_is_param():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    op1 = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="param")
    assert op.parameters[0].is_param is False
    assert op.parameters[1].is_param is False
    assert op.parameters[2].is_param
    assert op.parameters[3].is_param
    assert op.parameters[4].is_param is False
    assert op1.parameters[4].is_param


def test_Parameter_type_():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    op4 = OperatorFn.from_def(fn4, param_parser=mock_arg_parser, implicit="input")
    op5 = OperatorFn.from_def(fn5, param_parser=mock_arg_parser, implicit="input")
    assert op.parameters[0].type_ is int
    assert op.parameters[1].type_ is str
    assert op.parameters[2].type_ is str
    assert op.parameters[3].type_ is str
    assert op4.parameters[0].type_ is PydanticType
    assert op5.parameters[0].type_ is SomeType


def test_Parameter_name():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    assert op.parameters[0].name == "in1"
    assert op.parameters[1].name == "in2"
    assert op.parameters[2].name == "p1"
    assert op.parameters[3].name == "p2"


def test_Parameter_default():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    assert op.parameters[5].default == Parameter.empty
    assert op.parameters[6].default == "default"


def test_Parameter_is_positional_param():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    assert op.parameters[0].is_positional_param is False
    assert op.parameters[1].is_positional_param is False
    assert op.parameters[2].is_positional_param
    assert op.parameters[3].is_positional_param


def test_Parameter_is_keyword_param():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    assert op.parameters[5].is_keyword_param
    assert op.parameters[6].is_keyword_param


def test_Parameter_is_var_input():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    assert op.parameters[4].is_var_input


def test_Parameter_is_var_param():
    op1 = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="param")
    assert op1.parameters[4].is_var_param


def test_Parameter_is_var_keyword():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    assert op.parameters[7].is_var_keyword


def test_Parameter_description():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    assert op.parameters[5].description == "k1 doc"


def test_Parameter_is_required():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    op1 = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="param")
    assert op.parameters[0].is_required
    assert op.parameters[1].is_required
    assert op.parameters[2].is_required
    assert not op.parameters[3].is_required
    assert op.parameters[4].is_required
    assert not op1.parameters[4].is_required
    assert op.parameters[5].is_required
    assert not op.parameters[6].is_required


def test_Parameter_is_positional_only():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    assert op.parameters[0].kind == ParameterKind.POSITIONAL_ONLY
    assert op.parameters[1].kind == ParameterKind.POSITIONAL_ONLY
    assert op.parameters[2].kind == ParameterKind.POSITIONAL_ONLY
    assert op.parameters[3].kind == ParameterKind.POSITIONAL_ONLY


def test_Parameter_is_keyword_only():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    assert op.parameters[5].kind == ParameterKind.KEYWORD_ONLY
    assert op.parameters[6].kind == ParameterKind.KEYWORD_ONLY


def test_iter_positional():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    op2 = OperatorFn.from_def(fn2, param_parser=mock_arg_parser, implicit="input")
    iter_positional = op.parameters.iter_positional()
    assert next(iter_positional).name == "in1"
    assert next(iter_positional).name == "in2"
    assert next(iter_positional).name == "p1"
    assert next(iter_positional).name == "p2"
    assert next(iter_positional).name == "var_args"
    assert next(iter_positional).name == "var_args"
    with pytest.raises(StopIteration):
        next(op2.parameters.iter_positional())


def test_Parameters_required_kwds():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    required_kwds = op.parameters.required_keywords
    assert "k1" in required_kwds
    assert "k2" not in required_kwds


def test_Parameters_iter_positional_arguments():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    op1 = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="param")
    iter = op.parameters.iter_positional_arguments()
    iter1 = op1.parameters.iter_positional_arguments()
    assert next(iter).name == "p1"
    assert next(iter).name == "p2"
    with pytest.raises(StopIteration):
        next(iter)
    assert next(iter1).name == "in1"
    assert next(iter1).name == "p1"
    assert next(iter1).name == "p2"
    assert next(iter1).name == "var_args"
    assert next(iter1).name == "var_args"


def test_Parameters_iter_inputs():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    iter = op.parameters.iter_inputs()
    assert next(iter).name == "in1"
    assert next(iter).name == "in2"
    assert next(iter).name == "var_args"
    assert next(iter).name == "var_args"


def test_Parameters_get_keyword_argument():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    op1 = OperatorFn.from_def(fn1, param_parser=mock_arg_parser, implicit="input")
    assert op.parameters.get_keyword_argument("k1").name == "k1"
    assert op.parameters.get_keyword_argument("some").name == "var_kwds"
    with pytest.raises(KeyError):
        op1.parameters.get_keyword_argument("k1")


def test_Parameters_args():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    args = op.parameters.iter_positional_arguments()
    assert next(args).name == "p1"
    assert next(args).name == "p2"
    with pytest.raises(StopIteration):
        next(args)


def test_Parameters_var_argument():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    op1 = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="param")
    assert op.parameters.var_argument is None
    assert op1.parameters.var_argument.name == "var_args"


def test_Parameters_var_keyword():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    op1 = OperatorFn.from_def(fn1, param_parser=mock_arg_parser, implicit="input")
    assert op.parameters.var_keyword.name == "var_kwds"
    assert op1.parameters.var_keyword is None


def test_Parameters_num_inputs():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    op1 = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="param")
    assert op.parameters.num_minimum_inputs == 3
    assert op1.parameters.num_minimum_inputs == 1


def test_Parameters_input_present():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    input_present = op.parameters.input_present
    assert input_present


def test_Parameters_var_input():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    var_input = op.parameters.var_input
    assert var_input.name == "var_args"


def test_Parameters_num_required_args():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    op1 = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="param")
    num_required_args = op.parameters.num_required_args
    assert num_required_args == 1
    assert op1.parameters.num_required_args == 2


def test_ReturnValue_type_():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    op1 = OperatorFn.from_def(fn3, param_parser=mock_arg_parser, implicit="input")
    assert op.output.type_ is int
    assert op1.output.type_ is None


def test_ReturnValue_validator():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    assert isinstance(op.output.validator, TypeAdapter)


def test_ReturnValue_annotation():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    assert op.output.annotation == t.Annotated[int, Output()]


def test_ReturnValue_info():
    op = OperatorFn.from_def(fn, param_parser=mock_arg_parser, implicit="input")
    assert isinstance(op.output.info, Output)
