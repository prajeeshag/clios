# type: ignore

from dataclasses import dataclass

import pytest

from clios.exceptions import ChainTypeError, OperatorNotFound, TokenError
from clios.operation import Operation as Optn
from clios.operation import ReadOperation as ROptn
from clios.operation import WriteOperation as WOptn
from clios.operator import Operator as Op
from clios.operator import Reader as Rdr
from clios.operator import Writer as Wtr
from clios.operator._Operator import _Input as I
from clios.tokenizer import FilePathToken as Ft
from clios.tokenizer import OperatorToken as Ot


@dataclass
class Input:
    tkns: list[Ot]
    ops: list[Op]
    wtr: Wtr
    rdr: Rdr

    @property
    def expected(self):
        tkns = self.tkns[:]
        ops = self.ops[:]
        otkn = tkns.pop()
        rtkn = tkns.pop()
        optn = ROptn(self.rdr, rtkn.path)
        while tkns:
            tkn = tkns.pop()
            op = ops.pop()
            optn = Optn(op, (optn,), tkn.params, tkn.kwparams)
        return WOptn(self.wtr, optn, (otkn.path,))


@pytest.mark.parametrize(
    "input",
    [
        Input(
            [Ot("op"), Ft("fin"), Ft("fout")],
            [Op(None, output_type=int, input=I((int,)))],
            Wtr(None, int, 1),
            Rdr(None, int),
        ),
        Input(
            [
                Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                Ft("fin"),
                Ft("fout"),
            ],
            [Op(None, output_type=int, input=I((int,)))],
            Wtr(None, int, 1),
            Rdr(None, int),
        ),
        Input(
            [
                Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                Ot("op1", (), (("b", "2"), ("c", "3"))),
                Ft("fin"),
                Ft("fout"),
            ],
            2 * [Op(None, output_type=int, input=I((int,)))],
            Wtr(None, int, 1),
            Rdr(None, int),
        ),
        Input(
            [
                Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                Ot("op1", (), (("b", "2"), ("c", "3"))),
                Ot("op2"),
                Ft("fin"),
                Ft("fout"),
            ],
            [
                Op("op", output_type=int, input=I((int,))),
                Op("op1", output_type=int, input=I((int,))),
                Op("op2", output_type=int, input=I((str,))),
            ],
            Wtr(None, int, 1),
            Rdr(None, int),
        ),
    ],
)
def test(mocker, parser, input, operators, writers, readers):
    operators.get.side_effect = input.ops
    readers.get.return_value = input.rdr
    writers.get.return_value = input.wtr

    res = parser.parse_tokens(input.tkns)

    call = mocker.call
    operators.get.assert_has_calls([call(tkn.name) for tkn in input.tkns[0:-2]])
    operators.get.assert_has_calls(
        [call(tkn.name) for tkn in input.tkns[0:-2]], any_order=True
    )
    writers.get.assert_called_once_with(input.ops[0].output_type)
    readers.get.assert_has_calls(
        [call(input.ops[-1].input.dtypes[i]) for i in range(input.ops[-1].input.len)],
        any_order=False,
    )
    assert res == input.expected


@pytest.mark.parametrize(
    "input",
    [
        Input(
            [Ot("op"), Ft("fin")],
            [Op(None, output_type=int, input=I((int,)))],
            Wtr(None, int, 1),
            Rdr(None, int),
        ),
        Input(
            [
                Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                Ft("fout"),
            ],
            [Op(None, output_type=int, input=I((int,)))],
            Wtr(None, int, 1),
            Rdr(None, int),
        ),
        Input(
            [
                Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                Ot("op1", (), (("b", "2"), ("c", "3"))),
                Ft("fout"),
            ],
            2 * [Op(None, output_type=int, input=I((int,)))],
            Wtr(None, int, 1),
            Rdr(None, int),
        ),
        Input(
            [
                Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                Ot("op1", (), (("b", "2"), ("c", "3"))),
                Ot("op2"),
                Ft("fout"),
            ],
            3 * [Op(None, output_type=int, input=I((int,)))],
            Wtr(None, int, 1),
            Rdr(None, int),
        ),
    ],
)
def test_missing_input(parser, input, operators, writers, readers):
    operators.get.side_effect = input.ops
    readers.get.return_value = input.rdr
    writers.get.return_value = input.wtr

    with pytest.raises(TokenError) as e:
        parser.parse_tokens(input.tkns)

    assert str(e.value) == "Missing inputs"
    assert e.value.token == str(input.tkns[-2])


@pytest.mark.parametrize(
    "input,expected",
    [
        [
            Input(
                [Ot("op")],
                [Op(None, output_type=int, input=I((int,)))],
                Wtr(None, int, 1),
                Rdr(None, int),
            ),
            TokenError("-op", msg="Missing output"),
        ],
        [
            Input(
                [
                    Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                ],
                [Op(None, output_type=int, input=I((int,)))],
                Wtr(None, int, 1),
                Rdr(None, int),
            ),
            TokenError("-op,1,a,b=2,c=3", msg="Missing output"),
        ],
        [
            Input(
                [
                    Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                    Ft("fi"),
                    Ot("op1", ("a",)),
                ],
                [Op(None, output_type=int, input=I((int,)))],
                Wtr(None, int, 1),
                Rdr(None, int),
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
    readers.get.return_value = input.rdr
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
            [Op(None, output_type=int, input=I((int,)))],
            Wtr(None, int, 1),
            Rdr(None, int),
        ),
        Input(
            [
                Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                Ot("op1", (), (("b", "2"), ("c", "3"))),
                Ft("fin"),
                Ft("fout1"),
                Ft("fout2"),
            ],
            2 * [Op(None, output_type=int, input=I((int,)))],
            Wtr(None, int, 1),
            Rdr(None, int),
        ),
    ],
)
def test_too_many_inputs(mocker, parser, input, operators, writers, readers):
    operators.get.side_effect = input.ops
    readers.get.return_value = input.rdr
    writers.get.return_value = input.wtr

    with pytest.raises(TokenError) as e:
        parser.parse_tokens(input.tkns)

    assert str(e.value) == "Too many inputs"
    assert e.value.token == str(input.tkns[-2])


@pytest.mark.parametrize(
    "input, expected",
    [
        [
            Input(
                [Ot("op"), Ft("fin"), Ft("fout")],
                [KeyError()],
                Wtr(None, int, 1),
                Rdr(None, int),
            ),
            "op",
        ],
        [
            Input(
                [
                    Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                    Ot("op1", (), (("b", "2"), ("c", "3"))),
                    Ft("fin"),
                    Ft("fout2"),
                ],
                [Op(None, output_type=int, input=I((int,))), KeyError()],
                Wtr(None, int, 1),
                Rdr(None, int),
            ),
            "op1",
        ],
    ],
)
def test_operator_not_found(parser, input, operators, writers, readers, expected):
    operators.get.side_effect = input.ops
    readers.get.return_value = input.rdr
    writers.get.return_value = input.wtr

    with pytest.raises(OperatorNotFound) as e:
        parser.parse_tokens(input.tkns)

    assert e.value.operator == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        [
            Input(
                [
                    Ot("op", ("1", "a"), (("b", "2"), ("c", "3"))),
                    Ot("op1", (), (("b", "2"), ("c", "3"))),
                    Ft("fin"),
                    Ft("fout2"),
                ],
                [
                    Op(None, output_type=int, input=I((int,))),
                    Op(None, output_type=str, input=I((int,))),
                ],
                Wtr(None, int, 1),
                Rdr(None, int),
            ),
            ChainTypeError("op1", "op", int, str),
        ],
    ],
)
def test_chain_type_error(parser, input, operators, writers, readers, expected):
    operators.get.side_effect = input.ops
    readers.get.return_value = input.rdr
    writers.get.return_value = input.wtr

    with pytest.raises(ChainTypeError) as e:
        parser.parse_tokens(input.tkns)

    assert e.value.downstream_op == expected.downstream_op
    assert e.value.upstream_op == expected.upstream_op
    assert e.value.expected_type == expected.expected_type
    assert e.value.received_type == expected.received_type
