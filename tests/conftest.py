# type: ignore
import sys
from typing import Annotated

import pytest

from clios.cli.ast_builder import ASTBuilder
from clios.core.param_info import Input, Output, Param
from clios.registry import OperatorRegistry

intOut = Annotated[int, Output(file_saver=print)]


intParam = Annotated[int, Param()]
intIn = Annotated[int, Input()]

IntParam = Annotated[int, Param(core_validation_phase="execute")]
IntIn = Annotated[int, Input(core_validation_phase="execute")]


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


def op_vi(*i: intIn):
    pass


def op_1k(*, ip: intParam):
    pass


def op_1p(ip: intParam):
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
# for func in list_functions():
#     operators.add(func.__name__, get_operator_fn(func))


@pytest.fixture
def parser():
    return ASTBuilder(operators)


@pytest.fixture
def parser_execute():
    return ASTBuilder(operators)
