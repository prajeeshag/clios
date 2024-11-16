from enum import Enum
from typing import Any, TypedDict

from pydantic import ValidationError

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


class ErrorType(str, Enum):
    OPERATOR_NOT_FOUND = "Operator not found"
    UNSUPPORTED_ROOT_OPERATOR = "Unsupported root operator"
    MISSING_OUTPUT = "Missing output"
    MISSING_OUTPUT_FILE = "Missing output file"
    TOO_MANY_INPUTS = "Too many inputs"
    TOO_FEW_INPUTS = "Too few inputs"
    MISSING_INPUTS = "Missing inputs"
    TOO_MANY_ARGS = "Too many arguments"
    TOO_FEW_ARGS = "Too few arguments"
    MISSING_REQUIRED_KWD = "Missing required keyword argument"
    UNEXPECTED_KWD = "Unexpected keyword argument"
    CHAIN_TYPE_ERROR = "Cannot chain operator"
    ARG_VALIDATION_ERROR = "Argument validation error"
    INPUT_VALIDATION_ERROR = "Input validation error"
    SYNTAX_NOT_SUPPORTED = "Syntax not supported"


class ParserErrorCtx(TypedDict, total=False):
    token_index: int
    unchainable_token_index: int
    expected_num_args: int
    arg_key: str
    arg_index: int
    validation_error: ValidationError


class ParserError(Exception):
    def __init__(
        self,
        error_type: ErrorType,
        ctx: ParserErrorCtx = {},
    ) -> None:
        self.error_type = error_type
        self.ctx = ctx
        super().__init__(error_type.value)


class _Empty:
    pass


class ASTBuilder:
    def __init__(
        self,
        operators: OperatorRegistry,
    ) -> None:
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
            raise ParserError(ErrorType.OPERATOR_NOT_FOUND, ctx={"token_index": index})

        try:
            opfn = self._operators.get(op_token.name)
        except KeyError:
            raise ParserError(ErrorType.OPERATOR_NOT_FOUND, ctx={"token_index": index})

        num_outputs = 0
        file_saver = None
        if opfn.return_type.type_ is not None and not return_value:
            file_saver = opfn.return_type.info.file_saver
            if file_saver is None:
                raise ParserError(
                    ErrorType.UNSUPPORTED_ROOT_OPERATOR, ctx={"token_index": index}
                )
            num_outputs = opfn.return_type.info.num_outputs

        output_file_paths: list[str] = []
        for i in range(num_outputs):
            try:
                outputtkn = token_list.pop()
                if not isinstance(outputtkn, StringToken):
                    raise ParserError(
                        ErrorType.MISSING_OUTPUT_FILE,
                        ctx={"token_index": num_tokens - 1 - i},
                    )
                output_file_paths.append(str(outputtkn))
            except IndexError:
                raise ParserError(ErrorType.MISSING_OUTPUT, ctx={"token_index": index})

        token_list = list(reversed(token_list))

        operator = self._parse_tokens(token_list, op_token, opfn, index)

        if len(token_list) != 0:
            raise ParserError(
                ErrorType.TOO_MANY_INPUTS,
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
                if in_type is not Any and in_type != child_op.return_type.type_:
                    raise ParserError(
                        ErrorType.CHAIN_TYPE_ERROR,
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
                        ErrorType.INPUT_VALIDATION_ERROR,
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
                    ErrorType.SYNTAX_NOT_SUPPORTED,
                    ctx={"token_index": child_token_index},
                )

        if len(child_operators) < len(opfn.inputs):
            raise ParserError(ErrorType.MISSING_INPUTS, ctx={"token_index": index})

        if opfn.var_input is not None and (len(child_operators) - len(opfn.inputs)) < 1:
            raise ParserError(ErrorType.TOO_FEW_INPUTS, ctx={"token_index": index})

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
            raise ParserError(ErrorType.OPERATOR_NOT_FOUND, ctx={"token_index": index})
        return op


def _validate_operator_arguments(
    op_fn: OperatorFn,
    args: tuple[str, ...],
    index: int,
) -> tuple[Any, ...]:
    _verify_operator_arguments(op_fn, args, index)
    arg_values: list[Any] = []
    iter_args = op_fn.iter_args()
    for i, val in enumerate(args):
        param = next(iter_args)
        try:
            arg_values.append(param.validate_build(val))
        except ValidationError as e:
            raise ParserError(
                ErrorType.ARG_VALIDATION_ERROR,
                ctx={"token_index": index, "arg_index": i, "validation_error": e},
            )
    return tuple(arg_values)


def _verify_operator_arguments(op_fn: OperatorFn, args: tuple[str, ...], index: int):
    len_required_args = len(op_fn.required_args)
    if len(args) < len_required_args:
        raise ParserError(
            ErrorType.TOO_FEW_ARGS,
            ctx={"token_index": index, "expected_num_args": len_required_args},
        )
    if len(args) > len(op_fn.args) and op_fn.var_args is None:
        raise ParserError(
            ErrorType.TOO_MANY_ARGS,
            ctx={"token_index": index, "expected_num_args": len_required_args},
        )


def _validate_operator_keywords(
    op_fn: OperatorFn,
    kwds: tuple[KWd, ...],
    index: int,
) -> dict[str, Any]:
    kwds_dict = {kw.key: kw.val for kw in kwds}
    _verify_operator_keywords(op_fn, kwds_dict, index)
    arg_values: dict[str, Any] = {}
    for key, val in kwds_dict.items():
        param = op_fn.get_kwd(key)
        try:
            arg_values[key] = param.validate_build(val)
        except ValidationError as e:
            raise ParserError(
                ErrorType.ARG_VALIDATION_ERROR,
                ctx={"token_index": index, "arg_key": key, "validation_error": e},
            )
    return arg_values


def _verify_operator_keywords(op_fn: OperatorFn, kwds: dict[str, str], index: int):
    required_kwds_keys = op_fn.required_kwds.keys()
    kwds_keys = op_fn.kwds.keys()
    for key in required_kwds_keys:
        if key not in kwds:
            raise ParserError(
                ErrorType.MISSING_REQUIRED_KWD,
                ctx={"token_index": index, "arg_key": key},
            )
    if op_fn.var_kwds is None:
        for key in kwds:
            if key not in kwds_keys:
                raise ParserError(
                    ErrorType.UNEXPECTED_KWD, ctx={"token_index": index, "arg_key": key}
                )
