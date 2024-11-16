from typing import Any

from .exceptions import ArgumentError, ChainTypeError, OperatorNotFound, TokenError
from .operator.model import OperatorFn
from .operator.operator import (
    BaseOperator,
    LeafOperator,
    Operator,
    RootOperator,
    SimpleOperator,
)
from .registry import OperatorRegistry
from .tokenizer import KWd, OperatorToken, StringToken, Token


class ASTBuilder:
    def __init__(
        self,
        operators: OperatorRegistry,
    ) -> None:
        self._operators = operators

    def parse_tokens(self, tokens: tuple[Token, ...], index: int = 0) -> RootOperator:
        token_list = list(tokens)

        op_token = token_list[0]
        token_list.pop(0)

        if not isinstance(op_token, OperatorToken):
            raise OperatorNotFound(str(op_token))

        try:
            opfn = self._operators.get(op_token.name)
        except KeyError:
            raise OperatorNotFound(op_token.name)

        num_outputs = 0
        file_saver = None
        if opfn.return_type.type_ is not None:
            file_saver = opfn.return_type.info.file_saver
            if file_saver is None:
                raise TokenError(
                    str(op_token),
                    msg="""
                    This operator cannot be the root operator!
                    Use an operator that can save the output to a file.
                    if you just want to print the output, use the 'print' operator as the root operator.
                    """,
                )
            num_outputs = opfn.return_type.info.num_outputs

        output_file_paths: list[str] = []
        for _ in range(num_outputs):
            try:
                outputtkn = token_list.pop()
                if not isinstance(outputtkn, StringToken):
                    raise TokenError(
                        msg=f"Missing output file: got '{outputtkn}' instead of filename"
                    )
                output_file_paths.append(str(outputtkn))
            except IndexError:
                raise TokenError(str(op_token), msg="Missing output")

        token_list = list(reversed(token_list))

        operator = self._parse_tokens(token_list, op_token, opfn)

        if len(token_list) != 0:
            raise TokenError(str(token_list[-1]), msg="Too many inputs")

        return RootOperator(
            input=operator,
            file_saver=file_saver,
            args=tuple(output_file_paths),
        )

    def _parse_tokens(
        self,
        token_list: list[Token],
        opTkn: OperatorToken,
        opfn: OperatorFn,
    ) -> LeafOperator:
        validate_args = _validate_operator_arguments(opfn, opTkn.args)
        validate_kwds = _validate_operator_keywords(opfn, opTkn.kwds)

        if not opfn.input_present:
            return LeafOperator(opfn, args=validate_args, kwds=validate_kwds)

        child_operators: list[BaseOperator] = []

        for input_param in opfn.iter_inputs():
            if len(token_list) == 0:
                break
            tkn = token_list.pop()
            if isinstance(tkn, OperatorToken):
                child_op = self._get_operator(tkn)
                in_type = input_param.type_
                if in_type is not Any and in_type != child_op.return_type.type_:
                    raise ChainTypeError(
                        tkn.name,
                        opTkn.name,
                        input_param.type_,
                        child_op.return_type.type_,
                    )
                child_operator = self._parse_tokens(token_list, tkn, child_op)
                child_operators.append(child_operator)
            elif isinstance(tkn, StringToken):
                value = input_param.validate_build(tkn.value)
                child_operators.append(
                    SimpleOperator(input_param.validate_execute, value)
                )
            else:
                raise NotImplementedError

        if len(child_operators) < len(opfn.inputs):
            raise TokenError(str(opTkn), msg="Missing inputs")

        if opfn.var_input is not None and (len(child_operators) - len(opfn.inputs)) < 1:
            raise TokenError(str(opTkn), msg="Too few inputs")

        return Operator(
            operator_fn=opfn,
            inputs=tuple(child_operators),
            args=validate_args,
            kwds=validate_kwds,
        )

    def _get_operator(self, tkn: OperatorToken):
        try:
            op = self._operators.get(tkn.name)
        except KeyError:
            raise OperatorNotFound(tkn.name)
        return op


def _validate_operator_arguments(
    op_fn: OperatorFn, args: tuple[str, ...]
) -> tuple[Any, ...]:
    _verify_operator_arguments(op_fn, args)
    arg_values: list[Any] = []
    iter_args = op_fn.iter_args()
    for val in args:
        param = next(iter_args)
        arg_values.append(param.validate_build(val))
    return tuple(arg_values)


def _verify_operator_arguments(op_fn: OperatorFn, args: tuple[str, ...]):
    len_required_args = len(op_fn.required_args)
    if len(args) < len_required_args:
        raise ArgumentError(
            f"Expected at least {len_required_args} positional arguments, got {len(args)}"
        )
    if len(args) > len(op_fn.args) and op_fn.var_args is None:
        raise ArgumentError(
            f"Expected at most {len(op_fn.args)} arguments, got {len(args)}"
        )


def _validate_operator_keywords(
    op_fn: OperatorFn, kwds: tuple[KWd, ...]
) -> dict[str, Any]:
    kwds_dict = {kw.key: kw.val for kw in kwds}
    _verify_operator_keywords(op_fn, kwds_dict)
    arg_values: dict[str, Any] = {}
    for key, val in kwds_dict.items():
        param = op_fn.get_kwd(key)
        arg_values[key] = param.validate_execute(val)
    return arg_values


def _verify_operator_keywords(op_fn: OperatorFn, kwds: dict[str, str]):
    required_kwds_keys = op_fn.required_kwds.keys()
    kwds_keys = op_fn.kwds.keys()
    for key in required_kwds_keys:
        if key not in kwds:
            raise ArgumentError(f"Missing required keyword argument: {key}")
    if op_fn.var_kwds is None:
        for key in kwds:
            if key not in kwds_keys:
                raise ArgumentError(f"Unexpected keyword argument: {key}")
