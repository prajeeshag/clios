import importlib.util
import logging
import re
import typing as t
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from clios.core.main_parser import ParserAbc, ParserError
from clios.core.operator import (
    BaseOperator,
    DelegateOperator,
    LeafOperator,
    Operator,
    OperatorAbc,
    RootOperator,
    SimpleOperator,
)
from clios.core.operator_fn import OperatorFn, OperatorFns
from clios.core.param_parser import ParamParserError
from clios.core.tokenizer import Token

from .tokenizer import (
    CliTokenizer,
    LeftBracketToken,
    OperatorToken,
    RightBracketToken,
    StringToken,
    Tokenizer,
)

logger = logging.getLogger(__name__)


def simple_callback(value: t.Any) -> t.Any:
    return value


@dataclass(frozen=True)
class CliParser(ParserAbc):
    tokenizer: Tokenizer[list[str]] = CliTokenizer()

    def get_name(self, token: Token) -> str:
        if isinstance(token, OperatorToken):
            return token.value.split(",")[0].lstrip("-")
        return token.value

    def get_param_string(self, token: Token) -> str:
        if isinstance(token, OperatorToken):
            return ",".join(token.value.split(",")[1:])
        return ""

    def is_inline_operator(self, token: Token) -> bool:
        if isinstance(token, OperatorToken):
            name = Path(self.get_name(token)).name
            return self.is_inline_operator_name(name)
        return False

    def is_inline_operator_name(self, name: str) -> bool:
        pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*\.py$"
        return re.match(pattern, name) is not None

    def get_operator(
        self,
        operator_fns: OperatorFns,
        input: list[str],
        callback: t.Callable[..., t.Any] = simple_callback,
        **kwargs: t.Any,
    ) -> RootOperator:
        if not input:
            raise ParserError("Input is empty!")
        tokens = list(self.tokenizer.tokenize(input))
        num_tokens = len(tokens)
        token = tokens.pop(0)
        operator_name = self.get_name(token)
        param_string = self.get_param_string(token)
        operator_fn = self._get_operator_fn(operator_fns, token, 0)

        num_outputs = 0
        if operator_fn.output.type_ is not None:
            if operator_fn.output.info.callback is None:
                raise ParserError(
                    f"Operator `{operator_name}` cannot be used as root operator!",
                    ctx={"token_index": 0},
                )
            callback = operator_fn.output.info.callback
            num_outputs = operator_fn.output.info.num_outputs

        output_file_paths: list[str] = []
        for i in range(num_outputs):
            try:
                output_token = tokens.pop()
                if not isinstance(output_token, StringToken):
                    raise ParserError(
                        "Output file path must be a string",
                        ctx={"token_index": num_tokens - 1 - i},
                    )
                output_file_paths.append(str(output_token.value))
            except IndexError:
                raise ParserError(
                    "Missing output(s)!", ctx={"token_index": num_tokens - 1 - i}
                )

        tokens.reverse()

        operator = self._get_operator(
            operator_fns=operator_fns,
            operator_name=operator_name,
            param_string=param_string,
            operator_fn=operator_fn,
            token_index=0,
            input_tokens=tokens,
        )

        if len(tokens) != 0:
            raise ParserError(
                "Got too many inputs!",
                ctx={
                    "num_extra_tokens": len(tokens),
                    "token_index": num_tokens - len(tokens),
                },
            )

        return RootOperator(
            input=operator,
            callback=callback,
            args=tuple(output_file_paths),
        )

    def _get_operator(
        self,
        operator_fns: OperatorFns,
        operator_name: str,
        param_string: str,
        operator_fn: OperatorFn,
        token_index: int,
        input_tokens: list[Token],
    ) -> BaseOperator:
        try:
            logger.debug(
                f"parsing arguments for operator `{operator_name}`, param_string: {param_string}"
            )
            args, kwds = operator_fn.param_parser.parse_arguments(
                string=param_string,
                parameters=operator_fn.parameters,
            )
        except ParamParserError as e:
            raise ParserError(
                f"Failed to parse arguments for operator `{operator_name}`!",
                ctx={"error": e, "token_index": token_index},
            )

        if not operator_fn.parameters.input_present:
            return LeafOperator(
                name=operator_name,
                index=token_index,
                operator_fn=operator_fn,
                args=args,
                kwds=kwds,
            )

        if not input_tokens:
            raise ParserError(
                f"Missing inputs for operator {operator_name}!",
                ctx={"token_index": token_index},
            )
        operator_token_index = token_index
        num_tokens = len(input_tokens)
        if isinstance(input_tokens[-1], LeftBracketToken):
            # pop the left bracket
            input_tokens.pop()
            token_index += 1
            # get the child tokens until closing right bracket
            child_tokens = self._get_bracketed_tokens(input_tokens, token_index)
        else:
            child_tokens = input_tokens

        inputs = self._parse_inputs(
            operator_fns,
            operator_fn,
            token_index,
            operator_token_index,
            child_tokens,
        )

        token_index += num_tokens - len(input_tokens)

        if len(inputs) < operator_fn.parameters.num_minimum_inputs:
            raise ParserError(
                f"Missing inputs for operator {operator_name}!",
                ctx={"token_index": operator_token_index},
            )

        if operator_fn.is_delegate:
            return DelegateOperator(
                name=operator_name,
                index=operator_token_index,
                operator_fn=operator_fn,
                inputs=tuple(inputs),
                args=args,
                kwds=kwds,
            )

        return Operator(
            name=operator_name,
            index=token_index,
            operator_fn=operator_fn,
            inputs=tuple(inputs),
            args=args,
            kwds=kwds,
        )

    def _parse_inputs(
        self,
        operator_fns: OperatorFns,
        operator_fn: OperatorFn,
        token_index: int,
        operator_token_index: int,
        input_tokens: list[Token],
    ):
        if operator_fn.is_delegate:
            return self._parse_delegate_inputs(
                operator_fns,
                operator_fn,
                token_index,
                operator_token_index,
                input_tokens,
            )
        return self._parse_input_operators(
            operator_fns, operator_fn, token_index, operator_token_index, input_tokens
        )

    def _parse_delegate_inputs(
        self,
        operator_fns: OperatorFns,
        operator_fn: OperatorFn,
        token_index: int,
        operator_token_index: int,
        input_tokens: list[Token],
    ):
        inputs: list[str] = []

        child_index = token_index
        for input_param in operator_fn.parameters.iter_inputs():  # pragma: no cover
            if len(input_tokens) == 0:
                break
            child_token = input_tokens.pop()
            child_index += 1
            try:
                value = input_param.build_phase_validator.validate_python(
                    child_token.value
                )
            except ValidationError as e:
                raise ParserError(
                    f"Data validation failed for input {child_token.value}!",
                    ctx={"error": e, "token_index": child_index},
                )
            inputs.append(value)
        return inputs

    def _parse_input_operators(
        self,
        operator_fns: OperatorFns,
        operator_fn: OperatorFn,
        token_index: int,
        operator_token_index: int,
        input_tokens: list[Token],
    ):
        child_operators: list[OperatorAbc] = []

        child_index = token_index
        for input_param in operator_fn.parameters.iter_inputs():
            if len(input_tokens) == 0:
                break
            child_token = input_tokens.pop()
            child_index += 1
            if isinstance(child_token, OperatorToken):
                child_op_name = self.get_name(child_token)
                child_op_param_string = self.get_param_string(child_token)
                child_op_fn = self._get_operator_fn(
                    operator_fns, child_token, child_index
                )
                in_type = input_param.type_
                if in_type is not t.Any and in_type != child_op_fn.output.type_:
                    raise ParserError(
                        "These operators cannot be chained together!",
                        ctx={
                            "unchainable_token_index": child_index,
                            "token_index": operator_token_index,
                        },
                    )
                num_tokens_before = len(input_tokens)
                child_operator = self._get_operator(
                    operator_fns=operator_fns,
                    operator_name=child_op_name,
                    param_string=child_op_param_string,
                    operator_fn=child_op_fn,
                    token_index=child_index,
                    input_tokens=input_tokens,
                )
                child_operators.append(child_operator)
                child_index += num_tokens_before - len(input_tokens)
            elif isinstance(child_token, StringToken):
                try:
                    value = input_param.build_phase_validator.validate_python(
                        child_token.value
                    )
                except ValidationError as e:
                    raise ParserError(
                        f"Data validation failed for input {child_token.value}!",
                        ctx={"error": e, "token_index": child_index},
                    )
                child_operators.append(
                    SimpleOperator(
                        name=child_token.value,
                        index=child_index,
                        input_=value,
                    )
                )
            else:
                raise ParserError(
                    "This syntax is not supported yet!",
                    ctx={"token_index": child_index},
                )

        return child_operators

    def get_inline_operator_fn(self, name: str, index: int) -> OperatorFn:
        module_path = Path(name)
        module_name = module_path.stem
        try:
            module = load_module(module_name, module_path)
        except (ModuleNotFoundError, FileNotFoundError):
            raise ParserError(
                f"Module `{name}` not found!",
                ctx={"token_index": index},
            )
        operator_fn: OperatorFn | None = None

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, OperatorFn):
                if operator_fn is not None:
                    raise ParserError(
                        f"Multiple OperatorFn found in module `{name}`!",
                        ctx={"token_index": index},
                    )
                operator_fn = attr
        if operator_fn is None:
            raise ParserError(
                f"No OperatorFn found in module `{name}`!",
                ctx={"token_index": index},
            )
        return operator_fn

    def get_synopsis(
        self,
        operator_fn: OperatorFn,
        operator_name: str,
        command_name="",
        **kwds: t.Any,
    ) -> str:
        op = operator_fn
        param_synopsis = op.param_parser.get_synopsis(op.parameters, lsep=",")
        input_synopsis = " ".join([i.name for i in op.parameters if i.is_input])
        output_synopsis = " ".join(
            [f"output{i + 1}" for i in range(op.output.info.num_outputs)]
        )
        if op.output.info.num_outputs == 1:
            output_synopsis = "output"

        synopsis = command_name
        synopsis += f" -{operator_name}"
        if param_synopsis:
            synopsis += param_synopsis
        if input_synopsis:
            synopsis += f" {input_synopsis}"
        if output_synopsis:
            synopsis += f" {output_synopsis}"
        return synopsis

    def _get_operator_fn(
        self,
        operator_fns: OperatorFns,
        token: Token,
        index: int,
    ) -> OperatorFn:
        name = self.get_name(token)

        if self.is_inline_operator(token):
            return self.get_inline_operator_fn(name, index)

        op = operator_fns.get(name)
        if op is None:
            raise ParserError(
                f"Operator `{name}` not found!", ctx={"token_index": index}
            )
        return op

    def _get_bracketed_tokens(
        self, tokens: list[Token], opening_index: int
    ) -> list[Token]:
        """Get tokens until closing bracket is found"""
        bracket_stack: list[Token] = []
        token_stack: list[Token] = []
        while tokens:
            token = tokens.pop()
            token_stack.append(token)
            if isinstance(token, LeftBracketToken):
                bracket_stack.append(token)
            elif isinstance(token, RightBracketToken):
                if not bracket_stack:
                    return list(reversed(token_stack[:-1]))
                bracket_stack.pop()

        raise ParserError(
            "Missing closing bracket!",
            ctx={"token_index": opening_index},
        )


def load_module(module_name, path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
