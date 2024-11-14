# type: ignore
import pytest

from clios.operator.model import OperatorFn, Parameter, ParameterKind, ReturnType
from clios.operator.params import Input, Param


@pytest.fixture
def parameters():
    return (
        Parameter(
            name="input",
            kind=ParameterKind.POSITIONAL_ONLY,
            param_type=Input(strict=True),
            annotation=int,
        ),
        Parameter(
            name="var_input",
            kind=ParameterKind.POSITIONAL_ONLY,
            param_type=Input(strict=True),
            annotation=list[int],
        ),
        Parameter(
            name="positional_required",
            kind=ParameterKind.POSITIONAL_ONLY,
            param_type=Param(strict=False),
            annotation=str,
        ),
        Parameter(
            name="positional_optional",
            kind=ParameterKind.POSITIONAL_ONLY,
            param_type=Param(strict=False),
            annotation=str,
            default="default",
        ),
        Parameter(
            name="var_positional",
            kind=ParameterKind.VAR_POSITIONAL,
            param_type=Param(strict=False),
            annotation=list[int],
        ),
        Parameter(
            name="kwd_required",
            kind=ParameterKind.KEYWORD_ONLY,
            param_type=Param(strict=False),
            annotation=str,
        ),
        Parameter(
            name="kwd_optional",
            kind=ParameterKind.KEYWORD_ONLY,
            param_type=Param(strict=False),
            annotation=str,
            default="default",
        ),
        Parameter(
            name="var_keyword",
            kind=ParameterKind.VAR_KEYWORD,
            param_type=Param(strict=False),
            annotation=dict[str, str],
        ),
    )


@pytest.fixture
def return_type():
    return ReturnType(annotation=int)


@pytest.fixture
def operator_fn(parameters, return_type):
    def callback(*args, **kwargs):
        return sum(args)

    return OperatorFn(parameters=parameters, return_type=return_type, callback=callback)


def test_positional_params(operator_fn):
    positional_params = operator_fn.args
    assert len(positional_params) == 2
    assert positional_params[0].name == "positional_required"
    assert positional_params[1].name == "positional_optional"


def test_var_positional_param(operator_fn):
    var_positional_param = operator_fn.var_args
    assert var_positional_param.name == "var_positional"


def test_keyword_params(operator_fn):
    keyword_params = operator_fn.kwds
    assert len(keyword_params) == 2
    assert (keyword_params[0].name, keyword_params[1].name) == (
        "kwd_required",
        "kwd_optional",
    )


def test_var_keyword_param(operator_fn):
    var_keyword_param = operator_fn.var_kwds
    assert var_keyword_param is not None
    assert var_keyword_param.name == "var_keyword"


def test_inputs(operator_fn):
    inputs = operator_fn.inputs
    assert len(inputs) == 1
    assert inputs[0].name == "input"


def test_var_input(operator_fn):
    input = operator_fn.var_input
    assert input.name == "var_input"


def test_required_positional_params(operator_fn):
    required_positional_params = operator_fn.required_args
    assert len(required_positional_params) == 1
    assert required_positional_params[0].name == "positional_required"


def test_requiered_keyword_params(operator_fn):
    required_keyword_params = operator_fn.required_kwds
    assert len(required_keyword_params) == 1
    assert required_keyword_params[0].name == "kwd_required"
