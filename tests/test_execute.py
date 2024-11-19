# type: ignore
# import typing as t

# import pytest
# from pydantic import ValidationError

# from clios.cli.tokenizer import OperatorToken as Ot
# from clios.cli.tokenizer import StringToken as Ft
# from clios.core.operator import OperatorError, RootOperator
# from clios.core.param_info import Input, Output, Param

# intOut = t.Annotated[int, Output(file_saver=print)]


# intParam = t.Annotated[int, Param()]
# intIn = t.Annotated[int, Input()]

# IntParam = t.Annotated[int, Param(core_validation_phase="execute")]
# IntIn = t.Annotated[int, Input(core_validation_phase="execute")]


# def op_():
#     pass


# def op_1o_noroot() -> int:
#     pass


# def op_1i(i: intIn):
#     pass


# def op_1I(i: IntIn):
#     pass


# def op_2i(i: intIn, j: intIn):
#     pass


# def op_1o() -> intOut:
#     return 1


# def op_vi(*i: intIn):
#     pass


# def op_1k(*, ip: intParam):
#     pass


# def op_1p(ip: intParam):
#     pass


# def op_1K(*, ip: IntParam):
#     pass


# def op_1P(ip: IntParam):
#     pass


# def op_1p1o(ip: intParam) -> intOut:
#     return 1


# def op_1i1k(i: intIn, *, ip: intParam):
#     pass


# def op_1i1p(i: intIn, ip: intParam):
#     pass


# def op_1i1o(i: intIn) -> intOut:
#     return 1


# def op_1i1p1o(i: intIn, ip: intParam) -> intOut:
#     return 1


# def op_1i1k1o(i: intIn, *, ip: intParam) -> intOut:
#     return 1


# def list_functions():
#     current_module = sys.modules[__name__]
#     ff_functions = [
#         getattr(current_module, func)
#         for func in dir(current_module)
#         if func.startswith("op") and callable(getattr(current_module, func))
#     ]
#     return ff_functions


# operators = OperatorRegistry()
# # for func in list_functions():
# #     operators.add(func.__name__, get_operator_fn(func))


# @pytest.fixture
# def parser():
#     return ASTBuilder(operators)


# @pytest.fixture
# def parser_execute():
#     return ASTBuilder(operators)


# execute_validation_error = [
#     [
#         [Ot("op_1P,a")],
#         {
#             "error_type": "Data validation error!",
#             "token": Ot("op_1P,a"),
#             "arg_index": 0,
#         },
#     ],
#     [
#         [Ot("op_1K,ip=a")],
#         {
#             "error_type": "Data validation error!",
#             "token": Ot("op_1K,ip=a"),
#             "arg_key": "ip",
#         },
#     ],
#     [
#         [Ot("op_1I"), Ft("input")],
#         {
#             "error_type": "Data validation error!",
#             "token": Ft("input"),
#         },
#     ],
# ]


# @pytest.mark.parametrize("input,expected", execute_validation_error)
# def test_validation_error(parser, input, expected):
#     op = parser.parse_tokens(input)
#     with pytest.raises(OperatorError) as e:
#         op.execute()
#     assert str(e.value) == expected["error_type"]
#     assert e.value.ctx["token"] == expected["token"]
#     assert isinstance(e.value.ctx["validation_error"], ValidationError)
#     if "arg_index" in expected:
#         assert e.value.ctx["arg_index"] == expected["arg_index"]
#     elif "arg_key" in expected:
#         assert e.value.ctx["arg_key"] == expected["arg_key"]


# valid = [
#     [[Ot("op_")], "op_"],
#     [[Ot("op_1i"), Ot("op_1p1o,1")], "op_1i [ op_1p1o,1 ]"],
#     [
#         [Ot("op_1i1o"), Ot("op_1p1o,1"), Ft("output")],
#         "output [ op_1i1o [ op_1p1o,1 ] ]",
#     ],
#     [[Ot("op_1i"), Ft("100")], "op_1i [ 100 ]"],
# ]


# @pytest.mark.parametrize("input,expected_draw", valid)
# def test_valid(parser, input, expected_draw):
#     op = parser.parse_tokens(input)
#     assert isinstance(op, RootOperator)
#     assert op.draw() == expected_draw
#     op.execute()
