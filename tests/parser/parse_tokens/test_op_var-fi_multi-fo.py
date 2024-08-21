# type: ignore

from dataclasses import dataclass

import pytest

from clios.exceptions import TokenError
from clios.operation import GeneratorOperation as GOptn
from clios.operation import Operation as Optn
from clios.operation import ReadOperation as ROptn
from clios.operation import WriteOperation as WOptn
from clios.operator import Generator as Gn
from clios.operator import Operator as Op
from clios.operator import Reader as Rdr
from clios.operator import Writer as Wtr
from clios.operator._Operator import _Input as I
from clios.tokenizer import FilePathToken as Ft
from clios.tokenizer import OperatorToken as Ot


@dataclass
class Input:
    tkns: list[Ot]
    parent_op: Op
    child_ops_list: list[list[Op | Gn | Rdr]]
    wtr: Wtr

    @property
    def ops(self):
        res = [self.parent_op]
        for child_ops in self.child_ops_list:
            for child_op in child_ops:
                if not isinstance(child_op, Rdr):
                    res.append(child_op)
        return res

    @property
    def rdrs(self):
        res = []
        for child_ops in self.child_ops_list:
            for child_op in child_ops:
                if isinstance(child_op, Rdr):
                    res.append(child_op)
        return res

    def expected(self):
        ops_get_input = []
        readers_get_input = []
        tkns = list(self.tkns)
        otkns = []
        for _ in range(self.wtr.num_outputs):
            otkns.append(tkns.pop())

        otkns = reversed(otkns)

        child_opts = []
        for child_ops in reversed(self.child_ops_list):
            optn = None
            for child_op in reversed(child_ops):
                tkn = tkns.pop()
                if isinstance(child_op, Rdr):
                    optn = ROptn(child_op, tkn.path)
                    readers_get_input.append(child_op.dtype)
                elif isinstance(child_op, Gn):
                    optn = GOptn(child_op, tkn.params, tkn.kwparams)
                    ops_get_input.append(tkn.name)
                else:
                    optn = Optn(child_op, (optn,), tkn.params, tkn.kwparams)
                    ops_get_input.append(tkn.name)
            child_opts.append(optn)

        child_opts = reversed(child_opts)
        ops_get_input = reversed(ops_get_input)
        readers_get_input = reversed(readers_get_input)
        tkn = tkns.pop()
        optn = Optn(self.parent_op, tuple(child_opts), tkn.params, tkn.kwparams)
        fpaths = tuple(tkn.path for tkn in otkns)
        return (WOptn(self.wtr, optn, fpaths), ops_get_input, readers_get_input)


@pytest.mark.parametrize(
    "input",
    [
        Input(
            [Ot("op"), Ft("fi1"), Ft("fi2"), Ft("fi3"), Ft("fo")],
            Op(None, output_type=int, input=I((int,), True)),
            [[Rdr(None, int)], [Rdr(None, int)], [Rdr(None, int)]],
            Wtr(None, int, 1),
        ),
        Input(
            [Ot("op"), Ft("fi1"), Ft("fi2"), Ft("fo1"), Ft("fo2")],
            Op(None, output_type=int, input=I((int,), var_list=True)),
            [[Rdr(None, int)], [Rdr(None, int)]],
            Wtr(None, int, 2),
        ),
        Input(
            [Ot("op"), Ot("op1"), Ft("fi1"), Ot("op2"), Ft("fi2"), Ft("fi3"), Ft("fo")],
            Op("op", output_type=int, input=I((int,), True)),
            [
                [Op("op1", int, input=I((int,))), Rdr(None, int)],
                [Op("op2", int, input=I((int,))), Rdr(None, int)],
                [Rdr(None, int)],
            ],
            Wtr(None, int, 1),
        ),
        Input(
            [
                Ot("op"),
                Ot("op1"),
                Ft("fi1"),
                Ft("fi2"),
                Ot("op3", params=("x", "1")),
                Ft("fi3"),
                Ft("fo"),
            ],
            Op("op", output_type=int, input=I((int,), True)),
            [
                [Op("op1", int, input=I((int,))), Rdr(None, int)],
                [Rdr(None, int)],
                [Op("op3", int, input=I((float,))), Rdr(None, float)],
            ],
            Wtr(None, int, 1),
        ),
        Input(
            [
                Ot("op"),
                Ot("op1"),
                Ft("fi1"),
                Ot("gn1"),
                Ot("op2"),
                Ot("op2_1"),
                Ot("op3"),
                Ft("fi3"),
                Ft("fo"),
            ],
            Op("op", output_type=int, input=I((int,), True)),
            [
                [Op("op1", int, input=I((int,))), Rdr(None, int)],
                [Gn("gn1", int)],
                [
                    Op("op2", int, input=I((str,))),
                    Op("op2_1", str, input=I((int,))),
                    Op("op3", int, input=I((float,))),
                    Rdr(None, float),
                ],
            ],
            Wtr(None, int, 1),
        ),
        Input(
            [
                Ot("op"),
                Ot("op1"),
                Ft("fi1"),
                Ot("op2"),
                Ft("fi2"),
                Ot("op3"),
                Ft("fi3"),
                Ft("fo1"),
                Ft("fo2"),
                Ft("fo3"),
            ],
            Op("op", output_type=int, input=I((int,), True)),
            [
                [Op("op1", int, input=I((int,))), Rdr(None, int)],
                [Op("op2", int, input=I((int,))), Rdr(None, int)],
                [Op("op3", int, input=I((int,))), Rdr(None, int)],
            ],
            Wtr(None, int, 3),
        ),
    ],
)
def test(mocker, parser, input, operators, writers, readers):
    operators.get.side_effect = input.ops
    readers.get.side_effect = input.rdrs
    writers.get.return_value = input.wtr

    res = parser.parse_tokens(input.tkns)

    expected_optn, expected_ops_get_inputs, expected_readers_get_inputs = (
        input.expected()
    )

    call = mocker.call
    operators.get.assert_has_calls(
        [call(x) for x in expected_ops_get_inputs], any_order=False
    )
    operators.get.assert_has_calls(
        [call(x) for x in expected_ops_get_inputs], any_order=True
    )
    readers.get.assert_has_calls(
        [call(x) for x in expected_readers_get_inputs], any_order=False
    )
    readers.get.assert_has_calls(
        [call(x) for x in expected_readers_get_inputs], any_order=True
    )
    writers.get.assert_called_once_with(input.parent_op.output_type)
    assert res == expected_optn


@pytest.mark.parametrize(
    "input, expected",
    [
        [
            Input(
                [
                    Ot("op"),
                    Ot("op1"),
                    Ft("fi1"),
                    Ft("fi2"),
                    Ft("fi3"),
                    Ft("fo"),
                    Ft("fo1"),
                ],
                Op("op", output_type=int, input=I((int, str, float))),
                [
                    [Op("op1", int, input=I((int,))), Rdr(None, int)],
                    [Rdr(None, str)],
                    [Rdr(None, float)],
                ],
                Wtr(None, int, 1),
            ),
            "fo",
        ],
        [
            Input(
                [
                    Ot("op"),
                    Ot("op1"),
                    Ft("fi1"),
                    Ft("fi2"),
                    Ft("fi5"),
                    Ot("op3", params=("x", "1")),
                    Ft("fi3"),
                    Ft("fo"),
                ],
                Op("op", output_type=int, input=I((int, str, float))),
                [
                    [Op("op1", int, input=I((int,))), Rdr(None, int)],
                    [Rdr(None, str)],
                    [Op("op3", float, input=I((float,))), Rdr(None, float)],
                ],
                Wtr(None, int, 1),
            ),
            "-op3,x,1",
        ],
    ],
)
def test_too_many_inputs(expected, parser, input, operators, writers, readers):
    operators.get.side_effect = input.ops
    readers.get.side_effect = input.rdrs
    writers.get.return_value = input.wtr

    with pytest.raises(TokenError) as e:
        parser.parse_tokens(input.tkns)

    assert str(e.value) == "Too many inputs"
    assert e.value.token == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        [
            Input(
                [
                    Ot("op"),
                    Ot("op1"),
                    Ft("fi1"),
                    Ft("fi2"),
                    Ft("fo1"),
                ],
                Op("op", output_type=int, input=I((int, str, float))),
                [
                    [Op("op1", int, input=I((int,))), Rdr(None, int)],
                    [Rdr(None, str)],
                    [Rdr(None, float)],
                ],
                Wtr(None, int, 1),
            ),
            "-op",
        ],
        [
            Input(
                [
                    Ot("op", ("x", "2"), (("y", "3"),)),
                    Ot("op1"),
                    Ft("fi1"),
                    Ot("op2"),
                    Ft("fi2"),
                    Ft("fo"),
                ],
                Op("op", output_type=int, input=I((int, str, float))),
                [
                    [Op("op1", int, input=I((int,))), Rdr(None, int)],
                    [Op("op3", str, input=I((float,))), Rdr(None, float)],
                    [Rdr(None, float)],
                ],
                Wtr(None, int, 1),
            ),
            "-op,x,2,y=3",
        ],
    ],
)
def test_missing_inputs(expected, parser, input, operators, writers, readers):
    operators.get.side_effect = input.ops
    readers.get.side_effect = input.rdrs
    writers.get.return_value = input.wtr

    with pytest.raises(TokenError) as e:
        parser.parse_tokens(input.tkns)

    assert str(e.value) == "Missing inputs"
    assert e.value.token == expected
