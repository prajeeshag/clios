# type: ignore

from dataclasses import dataclass

import pytest

from clio.exceptions import ChainTypeError, TokenError
from clio.operation import GeneratorOperation as GOptn
from clio.operation import Operation as Optn
from clio.operation import WriteOperation as WOptn
from clio.operator import Generator as Gn
from clio.operator import Operator as Op
from clio.operator import Writer as Wtr
from clio.operator._Operator import _Input as I
from clio.tokenizer import FilePathToken as Ft
from clio.tokenizer import OperatorToken as Ot


@dataclass
class Input:
    tkns: list[Ot]
    ops: list[Op]
    wtr: Wtr

    @property
    def expected(self):
        tkns = self.tkns[:]
        ops = self.ops[:]
        otkn = tkns.pop()
        tkn = tkns.pop()
        op = ops.pop()
        optn = GOptn(op, tkn.params, tkn.kwparams)
        while tkns:
            tkn = tkns.pop()
            op = ops.pop()
            optn = Optn(op, (optn,), tkn.params, tkn.kwparams)
        return WOptn(self.wtr, optn, (otkn.path,))


@pytest.mark.parametrize(
    "input",
    [
        Input(
            [Ot("op"), Ft("fout")],
            [Gn("op", output_type=int)],
            Wtr(None, int, 1),
        ),
        Input(
            [
                Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                Ft("fout"),
            ],
            [Gn(None, output_type=int)],
            Wtr(None, int, 1),
        ),
        Input(
            [
                Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                Ot("op1", (), (("b", "2"), ("c", "3"))),
                Ft("fout"),
            ],
            [
                Op("op", output_type=int, input=I((int,))),
                Gn("op1", output_type=int),
            ],
            Wtr(None, int, 1),
        ),
        Input(
            [
                Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                Ot("op1", (), (("b", "2"), ("c", "3"))),
                Ot("op2"),
                Ft("fout"),
            ],
            [
                Op("op", output_type=int, input=I((int,))),
                Op("op1", output_type=int, input=I((int,))),
                Gn("op2", output_type=int),
            ],
            Wtr(None, int, 1),
        ),
    ],
)
def test(mocker, parser, input, operators, writers, readers):
    operators.get.side_effect = input.ops
    writers.get.return_value = input.wtr

    res = parser.parse_tokens(input.tkns)

    call = mocker.call
    operators.get.assert_has_calls([call(tkn.name) for tkn in input.tkns[0:-1]])
    operators.get.assert_has_calls(
        [call(tkn.name) for tkn in input.tkns[0:-1]], any_order=True
    )
    writers.get.assert_called_once_with(input.ops[0].output_type)
    readers.get.assert_not_called()
    assert res == input.expected


@pytest.mark.parametrize(
    "input,expected",
    [
        [
            Input(
                [Ot("op")],
                [Gn("op", output_type=int)],
                Wtr(None, int, 1),
            ),
            TokenError("-op", msg="Missing output"),
        ],
        [
            Input(
                [
                    Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                ],
                [Gn("op", output_type=int)],
                Wtr(None, int, 1),
            ),
            TokenError("-op,1,a,b=2,c=3", msg="Missing output"),
        ],
        [
            Input(
                [
                    Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                    Ot("op1", ("a",)),
                ],
                [Gn(None, output_type=int)],
                Wtr(None, int, 1),
            ),
            TokenError(
                "",
                msg="Missing output file: got '-op1,a' instead of filename",
            ),
        ],
    ],
)
def test_missing_output(expected, parser, input, operators, writers, readers):
    operators.get.side_effect = input.ops
    writers.get.return_value = input.wtr

    with pytest.raises(TokenError) as e:
        parser.parse_tokens(input.tkns)

    assert str(e.value) == str(expected)
    assert e.value.token == expected.token


@pytest.mark.parametrize(
    "input",
    [
        Input(
            [Ot("op"), Ft("fin"), Ft("fout"), Ft("fi")],
            [Gn(None, output_type=int)],
            Wtr(None, int, 1),
        ),
        Input(
            [
                Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                Ot("op1", (), (("b", "2"), ("c", "3"))),
                Ft("fin"),
                Ft("fout1"),
                Ft("fout2"),
            ],
            [
                Op("op", output_type=int, input=I((int,))),
                Gn("op1", output_type=int),
            ],
            Wtr(None, int, 1),
        ),
    ],
)
def test_too_many_inputs(mocker, parser, input, operators, writers, readers):
    operators.get.side_effect = input.ops
    writers.get.return_value = input.wtr

    with pytest.raises(TokenError) as e:
        parser.parse_tokens(input.tkns)

    assert str(e.value) == "Too many inputs"
    assert e.value.token == str(input.tkns[-3])


@pytest.mark.parametrize(
    "input, expected",
    [
        [
            Input(
                [
                    Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                    Ot("op1", (), (("b", "2"), ("c", "3"))),
                    Ft("fout2"),
                ],
                [
                    Op("op", output_type=int, input=I((int,))),
                    Gn("op1", output_type=str),
                ],
                Wtr(None, int, 1),
            ),
            ChainTypeError("op1", "op", int, str),
        ],
    ],
)
def test_chain_type_error(parser, input, operators, writers, readers, expected):
    operators.get.side_effect = input.ops
    writers.get.return_value = input.wtr

    with pytest.raises(ChainTypeError) as e:
        parser.parse_tokens(input.tkns)

    assert e.value.downstream_op == expected.downstream_op
    assert e.value.upstream_op == expected.upstream_op
    assert e.value.expected_type == expected.expected_type
    assert e.value.received_type == expected.received_type
