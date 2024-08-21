# type: ignore

from dataclasses import dataclass

import pytest

from clio.operation import GeneratorOperation as GOptn
from clio.operation import Operation as Optn
from clio.operation import ReadOperation as ROptn
from clio.operation import WriteOperation as WOptn
from clio.operator import Generator as Gn
from clio.operator import Operator as Op
from clio.operator import Reader as Rdr
from clio.operator import Writer as Wtr
from clio.operator._Operator import _Input as I
from clio.tokenizer import FilePathToken as Ft
from clio.tokenizer import OperatorToken as Ot


@dataclass
class Input:
    tkns: list[Ot]
    parent_op: Op
    child_ops_dict: dict[Op | Gn | Rdr, list[list[Op | Gn | Rdr]]]
    wtr: Wtr

    def ops_rdrs(self):
        ops = [self.parent_op]
        rdrs = []
        for op, child_ops_list in self.child_ops_dict.items():
            if not isinstance(op, Rdr):
                ops.append(op)
            else:
                rdrs.append(op)

            for child_ops in child_ops_list:
                for child_op in child_ops:
                    if not isinstance(child_op, Rdr):
                        ops.append(child_op)
                    else:
                        rdrs.append(child_op)
        return ops, rdrs

    def expected(self):
        ops_get_input = []
        readers_get_input = []
        tkns = list(self.tkns)
        otkns = []
        for _ in range(self.wtr.num_outputs):
            otkns.append(tkns.pop())

        otkns = reversed(otkns)

        child_opts1 = []
        for child_op1, child_ops_list in reversed(list(self.child_ops_dict.items())):
            child_opts = []
            for child_ops in reversed(child_ops_list):
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
            child_opts = tuple(reversed(child_opts))

            tkn = tkns.pop()

            if isinstance(child_op1, Rdr):
                optn = ROptn(child_op1, tkn.path)
                readers_get_input.append(child_op1.dtype)
            elif isinstance(child_op1, Gn):
                optn = GOptn(child_op1, tkn.params, tkn.kwparams)
                ops_get_input.append(tkn.name)
            else:
                optn = Optn(child_op1, child_opts, tkn.params, tkn.kwparams)
                ops_get_input.append(tkn.name)
            child_opts1.append(optn)

        child_opts1 = tuple(reversed(child_opts1))
        print(child_opts1)
        ops_get_input = reversed(ops_get_input)
        readers_get_input = reversed(readers_get_input)
        tkn = tkns.pop()
        optn = Optn(self.parent_op, child_opts1, tkn.params, tkn.kwparams)
        fpaths = tuple(tkn.path for tkn in otkns)
        return (WOptn(self.wtr, optn, fpaths), ops_get_input, readers_get_input)


@pytest.mark.parametrize(
    "input",
    [
        Input(
            [Ot("op"), Ft("fi1"), Ft("fo")],
            Op("op", output_type=int, input=I((int,))),
            {
                Rdr(None, int): [],
            },
            Wtr(None, int, 1),
        ),
        Input(
            [Ot("op"), Ot("op1"), Ft("fi1"), Ft("fo")],
            Op("op", output_type=int, input=I((int,))),
            {
                Op("op1", int, input=I((int,))): [
                    [Rdr(None, int)],
                ],
            },
            Wtr(None, int, 1),
        ),
        Input(
            [
                Ot("op"),
                Ot("op3"),
                Ot("op32"),
                Ft("fi3"),
                Ft("fo"),
            ],
            Op("op", output_type=int, input=I((float,))),
            {
                Op("op3", float, input=I((int,))): [
                    [Op("op32", int, input=I((int,))), Rdr(None, int)],
                ],
            },
            Wtr(None, int, 1),
        ),
        Input(
            [
                Ot("op"),
                Ot("op1"),
                Ot("op11"),
                Ot("op12"),
                Ft("fi1"),
                Ot("op2"),
                Ft("fi2"),
                Ot("op3"),
                Ot("op31"),
                Ot("op32"),
                Ft("fi3"),
                Ft("fo"),
            ],
            Op("op", output_type=int, input=I((int, str, float))),
            {
                Op("op1", int, input=I((int,))): [
                    [
                        Op("op11", int, input=I((int,))),
                        Op("op12", int, input=I((int,))),
                        Rdr(None, int),
                    ],
                ],
                Op("op2", str, input=I((int,))): [
                    [Rdr(None, int)],
                ],
                Op("op3", float, input=I((int,))): [
                    [
                        Op("op31", int, input=I((int,))),
                        Op("op32", int, input=I((int,))),
                        Rdr(None, int),
                    ],
                ],
            },
            Wtr(None, int, 1),
        ),
        Input(
            [
                Ot("op"),
                Ot("op1"),
                Ot("gn11"),
                Ot("op12"),
                Ft("fi1"),
                Ot("op2"),
                Ft("fi2"),
                Ft("fo"),
            ],
            Op("op", output_type=int, input=I((int, str))),
            {
                Op("op1", int, input=I((int, int))): [
                    [Gn("gn11", int)],
                    [Op("op12", int, input=I((int,))), Rdr(None, int)],
                ],
                Op("op2", str, input=I((int,))): [
                    [Rdr(None, int)],
                ],
            },
            Wtr(None, int, 1),
        ),
        Input(
            [
                Ot("op"),
                Ot("op1"),
                Ot("gn11"),
                Ot("op12"),
                Ft("fi1"),
                Ot("op2"),
                Ft("fi21"),
                Ft("fi22"),
                Ft("fo"),
            ],
            Op("op", output_type=int, input=I((int, str))),
            {
                Op("op1", int, input=I((int, int))): [
                    [Gn("gn11", int)],
                    [Op("op12", int, input=I((int,))), Rdr(None, int)],
                ],
                Op("op2", str, input=I((int, float))): [
                    [Rdr(None, int)],
                    [Rdr(None, float)],
                ],
            },
            Wtr(None, int, 1),
        ),
    ],
)
def test(mocker, parser, input, operators, writers, readers):
    ops, rdrs = input.ops_rdrs()
    operators.get.side_effect = ops
    readers.get.side_effect = rdrs
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
