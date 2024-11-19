import typing as t

from pydantic import ValidationError

from clios.core.parameter import ParamVal
from clios.exceptions import ParserError

from ..core.operator import (
    BaseOperator,
    LeafOperator,
    Operator,
    RootOperator,
    SimpleOperator,
)
from ..core.operator_fn import OperatorFn
from ..registry import OperatorRegistry
from .tokenizer import OperatorToken, StringToken, Token


class _Empty:
    pass


class ASTBuilder:
    def __init__(self, operators: OperatorRegistry) -> None:
        self._operators = operators

    def parse_tokens(
        self,
        tokens: tuple[Token, ...],
        return_value: bool = False,
    ) -> RootOperator | _Empty:
        index = 0
        token_list = list(tokens)
        num_tokens = len(token_list)

        if num_tokens == 0:
            return _Empty()

        op_token = token_list[0]
        token_list.pop(0)

        if not isinstance(op_token, OperatorToken):
            raise ParserError(
                f"Operator `{op_token}` not found!", ctx={"token_index": index}
            )

        try:
            opfn = self._operators.get(op_token.name)
        except KeyError:
            raise ParserError(
                f"Operator `{op_token.name}` not found!", ctx={"token_index": index}
            )

        num_outputs = 0
        file_saver = None
        if opfn.output.type_ is not None and not return_value:
            file_saver = opfn.output.info.file_saver
            if file_saver is None:
                raise ParserError(
                    f"Operator `{op_token.name}` cannot be used as root operator!",
                    ctx={"token_index": index},
                )
            num_outputs = opfn.output.info.num_outputs

        output_file_paths: list[str] = []
        for i in range(num_outputs):
            try:
                outputtkn = token_list.pop()
                if not isinstance(outputtkn, StringToken):
                    raise ParserError(
                        "Output file path must be a string",
                        ctx={"token_index": num_tokens - 1 - i},
                    )
                output_file_paths.append(str(outputtkn))
            except IndexError:
                raise ParserError("Missing output(s)!", ctx={"token_index": index})

        token_list = list(reversed(token_list))

        operator = self._parse_tokens(token_list, op_token, opfn, index)

        if len(token_list) != 0:
            raise ParserError(
                "Got too many inputs!",
                ctx={"token_index": num_tokens - len(token_list)},
            )

        return RootOperator(
            input=operator,
            file_saver=file_saver,
            args=tuple(output_file_paths),
            return_value=return_value,
        )

    def _parse_tokens(
        self,
        token_list: list[Token],
        op_token: OperatorToken,
        opfn: OperatorFn,
        index: int,
    ) -> LeafOperator:
        validate_args = _validate_operator_arguments(opfn, op_token.args, index)
        validate_kwds = _validate_operator_keywords(opfn, op_token.kwds, index)

        if not opfn.input_present:
            return LeafOperator(op_token, opfn, args=validate_args, kwds=validate_kwds)

        child_operators: list[BaseOperator] = []

        child_token_index = index
        for input_param in opfn.iter_inputs():
            if len(token_list) == 0:
                break
            tkn = token_list.pop()
            child_token_index += 1
            if isinstance(tkn, OperatorToken):
                child_op = self._get_operator(tkn, child_token_index)
                in_type = input_param.type_
                if in_type is not t.Any and in_type != child_op.output.type_:
                    raise ParserError(
                        "These operators cannot be chained together!",
                        ctx={
                            "token_index": index,
                            "unchainable_token_index": child_token_index,
                        },
                    )
                num_tokens_before = len(token_list)
                child_operator = self._parse_tokens(
                    token_list, tkn, child_op, child_token_index
                )
                child_operators.append(child_operator)
                child_token_index += num_tokens_before - len(token_list)
            elif isinstance(tkn, StringToken):
                try:
                    value = input_param.validate_build(tkn.value)
                except ValidationError as e:
                    raise ParserError(
                        "Data validation error!",
                        ctx={
                            "token_index": child_token_index,
                            "validation_error": e,
                        },
                    )
                child_operators.append(
                    SimpleOperator(tkn, input_param.validate_execute, value)
                )
            else:
                raise ParserError(
                    "This syntax is not supported yet!",
                    ctx={"token_index": child_token_index},
                )

        if len(child_operators) < len(opfn.inputs):
            raise ParserError("Missing inputs!", ctx={"token_index": index})

        if opfn.var_input is not None and (len(child_operators) - len(opfn.inputs)) < 1:
            raise ParserError("Missing inputs!", ctx={"token_index": index})

        return Operator(
            op_token,
            operator_fn=opfn,
            inputs=tuple(child_operators),
            args=validate_args,
            kwds=validate_kwds,
        )

    def _get_operator(self, tkn: OperatorToken, index: int):
        try:
            op = self._operators.get(tkn.name)
        except KeyError:
            raise ParserError(
                f"Operator `{tkn.name}` not found!", ctx={"token_index": index}
            )
        return op


def _validate_operator_arguments(
    op_fn: OperatorFn,
    args: tuple[str, ...],
    index: int,
) -> tuple[t.Any, ...]:
    _verify_operator_arguments(op_fn, args, index)
    arg_values: list[t.Any] = []
    iter_args = op_fn.iter_positional_arguments()
    for i, val in enumerate(args):
        param = next(iter_args)
        try:
            arg_values.append(param.validate_build(val))
        except ValidationError as e:
            raise ParserError(
                "Data validation error!",
                ctx={"token_index": index, "arg_index": i, "validation_error": e},
            )
    return tuple(arg_values)


def _verify_operator_arguments(op_fn: OperatorFn, args: tuple[str, ...], index: int):
    len_required_args = len(op_fn.required_args)
    if len(args) < len_required_args:
        raise ParserError(
            f"Missing arguments: expected atleast {len_required_args}, got {len(args)}",
            ctx={"token_index": index},
        )
    if len(args) > len(op_fn.args) and op_fn.var_args is None:
        raise ParserError(
            f"Too many arguments: expected {len_required_args}, got {len(args)}",
            ctx={"token_index": index},
        )


def _validate_operator_keywords(
    op_fn: OperatorFn,
    kwds: tuple[ParamVal, ...],
    index: int,
) -> dict[str, t.Any]:
    kwds_dict = {kw.key: kw.val for kw in kwds}
    _verify_operator_keywords(op_fn, kwds_dict, index)
    arg_values: dict[str, t.Any] = {}
    for key, val in kwds_dict.items():
        param = op_fn.get_keyword_argument(key)
        try:
            arg_values[key] = param.validate_build(val)
        except ValidationError as e:
            raise ParserError(
                "Data validation error!",
                ctx={"token_index": index, "arg_key": key, "validation_error": e},
            )
    return arg_values


def _verify_operator_keywords(op_fn: OperatorFn, kwds: dict[str, str], index: int):
    required_kwds_keys = op_fn.required_kwds.keys()
    kwds_keys = op_fn.kwds.keys()
    for key in required_kwds_keys:
        if key not in kwds:
            raise ParserError(
                f"Missing required keyword argument: `{key}`!",
                ctx={"token_index": index, "arg_key": key},
            )
    if op_fn.var_kwds is None:
        for key in kwds:
            if key not in kwds_keys:
                raise ParserError(
                    f"Unknown keyword argument: `{key}`!",
                    ctx={"token_index": index, "arg_key": key},
                )
