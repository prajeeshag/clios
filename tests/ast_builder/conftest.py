# type: ignore
import sys
from typing import Annotated

import pytest

from clios.ast_builder import ASTBuilder
from clios.operator.params import Output, Param
from clios.operator.utils import get_operator_fn
from clios.registry import OperatorRegistry

intParam = Annotated[int, Param()]
intOut = Annotated[int, Output(file_saver=print)]


def op_():
    pass


def op_1o_noroot() -> int:
    pass


def op_1i(i: int):
    pass


def op_2i(i: int, j: int):
    pass


def op_1o() -> intOut:
    pass


def op_vi(*i: int):
    pass


def op_1k(*, ip: intParam):
    pass


def op_1p(ip: intParam):
    pass


def op_1i1k(i: int, *, ip: intParam):
    pass


def op_1i1p(i: int, ip: intParam):
    pass


def op_1i1o(i: int) -> intOut:
    return 1


def op_1i1p1o(i: int, ip: intParam) -> intOut:
    return 1


def op_1i1k1o(i: int, *, ip: intParam) -> intOut:
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
    operators.add(func.__name__, get_operator_fn(func))


@pytest.fixture
def parser():
    return ASTBuilder(operators)
